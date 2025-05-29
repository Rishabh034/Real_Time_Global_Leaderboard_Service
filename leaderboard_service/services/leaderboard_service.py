import time
import uuid


from leaderboard_service.services.leaderboard_model_service import LeaderBoardModelService
import heapq
import redis, pickle
from datetime import datetime, timedelta

LIMIT = 100
redis_client = redis.Redis()

class LeaderBoardService:

    def __init__(self,k):
        self.__leaderboard_model_service = LeaderBoardModelService()
        self.k = k
        self.heap = []  # min-heap: (score, timestamp, user_id)
        self.user_scores = {}  # user_id -> (score, timestamp)
        self.leaderboards = {}  # game_id -> {'heap': [...], 'user_scores': {...}}

    def save_leaderboard(self,heap, user_scores):
        redis_client.set("heap", pickle.dumps(heap))
        redis_client.set("user_scores", pickle.dumps(user_scores))

    def load_leaderboard(self):
        self.heap = pickle.loads(redis_client.get("heap") or b'[]')
        self.user_scores = pickle.loads(redis_client.get("user_scores") or b'{}')
        return self.heap, self.user_scores

    def _init_game_if_missing(self, game_id):
        if game_id not in self.leaderboards:
            self.leaderboards[game_id] = {
                'heap': [],
                'user_scores': {}
            }

    def current_timestamp(self):
        return time.time()

    def create_user(self,data):
        data = {
            "user_id": uuid.uuid4(),
            "user_name": data.get("user_name")
        }
        self.__leaderboard_model_service.create_user(data)

    def create_game(self, data):
        data = {
            "game_id": uuid.uuid4(),
            "game_name": data.get("game_name")
        }
        self.__leaderboard_model_service.create_game(data)


    def create_score(self, data):
        user_id = data.get("user_id")
        score = data.get("score")
        game_id = data.get("game_id")
        timestamp = self.current_timestamp()
        old = self.user_scores.get(user_id)
        # Only update if score is new or better
        self.load_leaderboard()
        self._init_game_if_missing(game_id)
        if old is None or score > old[0]:
            self.user_scores[user_id] = (score, timestamp)
            heapq.heappush(self.heap, (score, timestamp, user_id))

            # Trim if over K
            if len(self.heap) > self.k * 2:
                self.cleanup_heap()

        data = {
            "game_id": data.get("game_id"),
            "user_id": data.get("user_id"),
            "score": data.get("score"),
        }
        self.save_leaderboard(heap=self.heap,user_scores=self.user_scores)
        print("heap",self.heap)
        print("user scores",self.user_scores)
        self.__leaderboard_model_service.create_score(data)


    def cleanup_heap(self):
        # Remove stale entries to maintain K valid items
        new_heap = []
        first_score_timestamp = datetime.now() - timedelta(hours=24)
        for entry in self.heap:
            score, timestamp, user_id = entry
            if first_score_timestamp.timestamp() <= timestamp:
                continue
            if self.user_scores.get(user_id) == (score, timestamp):
                new_heap.append(entry)
        heapq.heapify(new_heap)
        self.heap = new_heap
        # Trim if still > K
        while len(self.heap) > self.k:
            score, timestamp, user_id = heapq.heappop(self.heap)
            if self.user_scores.get(user_id) == (score, timestamp):
                del self.user_scores[user_id]




    def get_top_k_leaders(self):
        self.load_leaderboard()
        self.cleanup_heap()
        # Return sorted by score descending
        # user id -> score , timestamp
        # 40,40,40
        top_users = sorted(self.user_scores.items(), key=lambda x: (-x[1][0], x[1][1]))
        if len(top_users) < LIMIT:
            self.get_data_from_database()
            top_users = sorted(self.user_scores.items(), key=lambda x: (-x[1][0], x[1][1]))
        return [(user_id, score) for user_id, (score, _) in top_users[:self.k]]


    def get_data_from_database(self):
        objs = self.__leaderboard_model_service.get_data_for_leaderboard()
        # This is fallback, if Node crash then we can take backup of data
        # We have fetched the recent data from scores and trying to fill our in memory database
        # to achieve minimum latency
        for obj in objs:
            user_id = obj.get('user_id')
            score = obj.get('score')
            timestamp = obj.get('timestamp')
            timestamp = timestamp.timestamp()
            self.user_scores[user_id] = (score, timestamp)
            heapq.heappush(self.heap, (score, timestamp, user_id))
