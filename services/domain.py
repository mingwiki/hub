import json

from models import t_domain


class DomainTreeManager:
    def __init__(self):
        self.db = t_domain
        self.tree = self._load_latest()

    def _load_latest(self):
        recs = self.db.all()
        if not recs:
            return {}
        t = recs[-1]["tree"]
        return json.loads(t) if isinstance(t, str) else t

    def _save(self):
        self.db.insert({"tree": self.tree})

    def _add(self, domain):
        parts = domain.split(".")[::-1]
        node = self.tree
        for p in parts:
            node = node.setdefault(p, {})

    def _delete(self, domain):
        parts = domain.split(".")[::-1]
        nodes = [self.tree]
        for p in parts:
            nxt = nodes[-1].get(p)
            if nxt is None:
                return
            nodes.append(nxt)
        for i in range(len(parts) - 1, -1, -1):
            parent, key = nodes[i], parts[i]
            if not parent[key]:
                del parent[key]
            else:
                break

    def batch(self, adds, dels):
        for d in dels:
            self._delete(d)
        for d in adds:
            self._add(d)
        self._save()

    def list_full_domains(self):
        results = []

        def walk(node, parts):
            if not node:
                results.append(".".join(parts[::-1]))
            else:
                for key in sorted(node):
                    walk(node[key], parts + [key])

        walk(self.tree, [])

        # Sort by right part first (e.g. com, example), then by leftmost (subdomain)
        results.sort(key=lambda d: (d.split(".")[::-1], d.split(".")[0]))
        return results
