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
        self.leaderboard = {}  # game_id -> {'heap': [...], 'user_scores': {...}}

    def save_leaderboard(self, leaderboard,game_id):
        heap = leaderboard[game_id]['heap']
        user_scores = leaderboard[game_id]['user_scores']
        redis_client.set(f"heap:{game_id}", pickle.dumps(heap) or b'[]')
        redis_client.set(f"user_scores:{game_id}", pickle.dumps(user_scores) or b'{}')

    def load_leaderboard(self,game_id):
        try:
            self.heap = pickle.loads(redis_client.get(f"heap:{game_id}"))
            self.user_scores = pickle.loads(redis_client.get(f"user_scores:{game_id}"))
        except Exception as e:
            print(f"Error occured in loading the leaderboard from redis: {e}")
            self.heap = []
            self.user_scores = {}
        finally:
            return self.heap, self.user_scores

    def _init_game_if_missing(self, game_id):
        if game_id not in self.leaderboard:
            self.leaderboard[game_id] = {
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
        import pdb
        pdb.set_trace()
        user_id = data.get("user_id")
        score = data.get("score")
        game_id = data.get("game_id")
        timestamp = self.current_timestamp()
        old = self.user_scores.get(user_id)
        # Only update if score is new or better
        self.load_leaderboard(game_id=game_id)
        self._init_game_if_missing(game_id)
        # fetching the game , if the game exist in leaderboard data structure
        game_data = self.leaderboard[game_id]
        if old is None or score > old[0]:
            heapq.heappush(self.heap, (score, timestamp, user_id))
            game_data['heap'] = self.heap
            game_data['user_scores'][user_id] = (score, timestamp)

            # Trim if over K
            if len(game_data['heap']) > self.k * 2:
                self.cleanup_heap()

        data = {
            "game_id": data.get("game_id"),
            "user_id": data.get("user_id"),
            "score": data.get("score"),
        }
        self.save_leaderboard(leaderboard=self.leaderboard,game_id=game_id)
        print("heap",self.heap)
        print("user scores",self.leaderboard[game_id]['user_score'])
        print("leaderboard",self.leaderboard)
        self.__leaderboard_model_service.create_score(data)


    def cleanup_heap(self):
        # Remove stale entries to maintain K valid items
        new_heap = []
        first_score_timestamp = datetime.now() - timedelta(hours=24)
        for entry in self.heap:
            score, timestamp, user_id = entry
            if first_score_timestamp.timestamp() > timestamp:
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



    def get_top_k_leaders(self,game_id,window_hours=None):
        self.heap, self.user_scores = self.load_leaderboard(game_id=game_id)
        print(self.heap)
        print(self.user_scores)
        print(self.leaderboard)
        self.cleanup_heap()
        # Return sorted by score descending
        # user id -> score , timestamp
        # 40,40,40
        print(self.heap)
        print(self.user_scores)
        latest_user_scores = self.user_scores.items()
        if window_hours:
            latest_user_scores = self.get_filter_data_based_on_window_hours(window_hours=window_hours)
        top_users = sorted(latest_user_scores, key=lambda x: (-x[1][0], x[1][1]))
        if len(top_users) < LIMIT:
            # it means top users are less than the k or limit
            # or may be node has crash in that case we will load our leaderboard
            # from our database
            self.get_data_from_database()
            top_users = sorted(latest_user_scores, key=lambda x: (-x[1][0], x[1][1]))
        return [(user_id, score) for user_id, (score, _) in top_users[:self.k]]


    def get_data_from_database(self,window_hours=None):

        if window_hours:
            cutoff = time.time() - window_hours * 3600
            objs = self.__leaderboard_model_service.get_data_for_leaderboard_for_window(cutoff_time=cutoff)
        else:
            objs = self.__leaderboard_model_service.get_data_for_leaderboard()

        # This is fallback, if Node crash then we can take backup of data
        # We have fetched the recent data from scores and trying to fill our in memory database
        # to achieve minimum latency
        for obj in objs:
            user_id = obj.get('user_id')
            score = obj.get('score')
            timestamp = obj.get('timestamp')
            game_id = obj.get('game_id')
            timestamp = timestamp.timestamp()
            self.user_scores[user_id] = (score, timestamp)
            heapq.heappush(self.heap, (score, timestamp, user_id))
            self._init_game_if_missing(game_id=game_id)
            self.leaderboard[game_id] = {
                'user_scores' : self.user_scores,
                'heap': self.heap
            }


    # This function is used for find user rank and its percentile
    def get_user_rank_and_percentile(self, game_id, user_id, window_hours = None):
        # Load leaderboard for this game
        heap, user_scores = self.load_leaderboard(game_id)
        # import pdb
        # pdb.set_trace()

        if user_id not in user_scores:
            return {"error": "User not found in leaderboard"}

        latest_user_scores = user_scores.items()
        if window_hours:
            latest_user_scores = self.get_filter_data_based_on_window_hours(window_hours=window_hours)
        # Sort by score desc, timestamp asc
        sorted_users = sorted(
            latest_user_scores, key=lambda x: (-x[1][0], x[1][1])
        )

        # Find rank (1-based)
        rank = next((i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id), None)
        total_users = len(sorted_users)

        if rank is None:
            return {"error": "User not ranked"}

        # Calculate percentile
        percentile = round((1 - (rank - 1) / total_users) * 100, 2)

        return {
            "user_id": user_id,
            "game_id": game_id,
            "rank": rank,
            "percentile": percentile
        }

    def get_filter_data_based_on_window_hours(self,window_hours):
        import pdb
        pdb.set_trace()
        if window_hours:
            # Filter by time window
            cutoff = time.time() - float(window_hours) * 3600
            filtered = [(uid, (score, ts)) for uid, (score, ts) in self.user_scores.items() if ts >= cutoff]
        else:
            filtered = self.user_scores.items()
        return filtered

