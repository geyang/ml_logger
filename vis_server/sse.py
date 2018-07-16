# SSE "protocol" is described here: http://mzl.la/UPFyxY
class ServerSentEvent(object):

    def __init__(self, data):
        self.data = data
        self.event = None
        self.id = None
        self.desc_map = {
            self.data: "data",
            self.event: "event",
            self.id: "id"
        }

    def __str__(self):
        if not self.data:
            return ""
        lines = [f"{v}: {k}" for k, v in self.desc_map.items() if k]
        return "%s\n\n" % "\n".join(lines)
