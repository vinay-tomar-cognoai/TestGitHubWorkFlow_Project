from locust import HttpLocust, TaskSet


def querydata(locust_obj):
    locust_obj.client.post("/chat/query/", {
        "user_id": "",
        "message": "how many leaves are allow in a year",
        "channel": "web"})


def renderiframe(locust_obj):
    locust_obj.client.get("/chat/bot")


def mis_dashboard(locust_obj):
    locust_obj.client.get("/chat/mis_dashboard")


def analytics(locust_obj):
    locust_obj.client.get("/chat/analytics")


class UserBehavior(TaskSet):
    tasks = {renderiframe: 3, mis_dashboard: 2, analytics: 1}

    def on_start(self):
        querydata(self)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
