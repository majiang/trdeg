PLAYER_PER_TABLE = 4

from enum import Enum, auto
from logging import getLogger
logger = getLogger(__name__)

class TableRank(Enum):

    PAN = auto()
    JOU = auto()
    TOK = auto()
    HOU = auto()


class TableKind(Enum):

    HAN4 = auto()
    TON4 = auto()
    HAN3 = auto()
    TON3 = auto()


class Table:

    def __init__(self, rank, kind):
        self._rank = rank
        self._kind = kind

    def rank(self):
        return self._rank

    def kind(self):
        return self._kind


class Player:

    def probability(self, table):
        raise NotImplementedError("Not implemented: Player.probability")


class Degree:

    def point(self, table):
        raise NotImplementedError("Not implemented: Degree.point")

    def index(self, point):
        import math
        from functools import reduce
        gcd = reduce(math.gcd, point)

        start = math.floor((self.start() - self.down()) / gcd) + 1
        up = math.ceil((self.up() - self.start()) / gcd) + start
        ret = {
            'down': 0,
            'start': start,
            'up': up,
        }
        logger.debug(str(sorted(list(ret.items()), key=(lambda kv: kv[1]))))
        ret['gcd'] = gcd
        return ret

    def start(self):
        raise NotImplementedError("Not implemented: Degree.start")

    def down(self):
        return 0

    def up(self):
        return self.start() * 2

class ConstantEfficiencyArithmeticProgression(Player):

    def __init__(self, efficiency):
        self._efficiency = efficiency

    def probability(self, table):
        rank = table.rank()
        if rank == TableRank.PAN:
            p, q = [20, 10]
        elif rank == TableRank.JOU:
            p, q = [40, 10]
        elif rank == TableRank.TOK:
            p, q = [50, 20]
        elif rank == TableRank.HOU:
            p, q = [60, 30]
        else:
            raise ValueError(f"Unknown table rank: {rank}")
        e = self._efficiency
        kind = table.kind()
        if kind == TableKind.HAN4 or TableKind.TON4:
            d = (p+q-10*e-20) / (12*p+4*q+120*e+240)
            assert 0 <= .25-3*d
            assert .25+3*d <= 1
            return [.25-3*d, .25-d, .25+d, .25+3*d]
        else:
            raise ValueError(f"Unknown table kind: {kind}")

    def __str__(self):
        return str(self._efficiency)

class Tenhou(Degree):

    def __init__(self, dan):
        self._dan = dan

    def point(self, table):
        rank = table.rank()
        if rank == TableRank.PAN:
            ret = [20, 10]
        elif rank == TableRank.JOU:
            ret = [40, 10]
        elif rank == TableRank.TOK:
            ret = [50, 20]
        elif rank == TableRank.HOU:
            ret = [60, 30]
        else:
            raise ValueError(f"Unknown table rank: {rank}")
        ret.append(0)
        ret.append((self._dan + 2) * -10)
        kind = table.kind()
        if kind == TableKind.HAN4:
            return [r * 3 // 2 for r in ret]
        elif kind == TableKind.TON4:
            return ret
        else:
            raise ValueError(f"Unknown table kind: {kind}")

    def start(self):
        return self._dan * 200

    def __str__(self):
        return str(self._dan)


def expectation(point, probability):
    return sum((pt * pr) for pt, pr in zip(point, probability))

from numpy import zeros
from numpy.linalg import solve

class Solver:
    def __init__(self, index, point, probability):
        assert index['down'] == 0
        assert 0 < sum(abs(pt * pr) for pt, pr in zip(point, probability))
        n = index['up'] + 1
        matrix = zeros((n, n))
        for i in range(1, n - 1):
            for pt, pr in zip(point, probability):
                dj = pt // index['gcd']
                j = max(min(i + dj, n-1), 0)
                matrix[i, j] -= pr
            matrix[i, i] += 1
        for i in (0, n - 1):
            matrix[i, i] += 1
        self._n = n
        self._matrix = matrix
        self._index = index

    def solve(self):

        class Result:

            def __init__(self, up_prob, up_count, down_prob, down_count):
                self.up_prob = up_prob
                self.up_count = up_count
                self.down_prob = down_prob
                self.down_count = down_count

            def __str__(self):
                return '\t'.join(map(str, [self.up_prob, self.up_count, self.down_prob, self.down_count]))

        return Result(self.up_prob(), self.up_count(), self.down_prob(), self.down_count())

    def probs(self, direction):
        vector = zeros(self._n)
        vector[self._index[direction]] = 1
        ret = solve(self._matrix, vector)
        assert ret[self._index[direction]] == 1
        return ret

    def up_probs(self):
        ret = self.probs('up')
        assert ret[self._index['down']] == 0
        return ret

    def down_probs(self):
        ret = self.probs('down')
        assert ret[self._index['up']] == 0
        return ret

    def prob(self, direction):
        return self.probs(direction)[self._index['start']]

    def up_prob(self):
        return self.prob('up')

    def down_prob(self):
        return self.prob('down')

    def count(self, direction):
        vector = self.probs(direction)
        vector[self._index[direction]] = 0
        prob = vector[self._index['start']]
        counts = solve(self._matrix, vector)
        assert counts[self._index[direction]] == 0
        return counts[self._index['start']] / prob

    def up_count(self):
        return self.count('up')

    def down_count(self):
        return self.count('down')

def main():
    while True:

        try:
            degree = Tenhou(int(input('dan? ')))
        except:
            break
        try:
            player = ConstantEfficiencyArithmeticProgression(float(input('efficiency? ')))
        except:
            break
        for rank in (TableRank.TOK, TableRank.HOU):
            for kind in (TableKind.HAN4, TableKind.TON4):
                table = Table(rank, kind)
                print(f"{rank} {kind}: {player.probability(table)}")

        for rank in (TableRank.TOK, TableRank.HOU):
            for kind in (TableKind.HAN4, TableKind.TON4):
                print(f"rank: {rank}; kind: {kind}")
                table = Table(rank, kind)
                point = degree.point(table)
                print(f"point: {point}")
                probability = player.probability(table)
                print(f"probs: {probability}")
                print(f"E[pt]: {expectation(point, probability)}")
                index = degree.index(point)
                print(f"index: {index}")
                solver = Solver(index, point, probability)
                print(f"up/dn: {solver.up_prob()}/{solver.down_prob()}")
                print(f"count: {solver.up_count()}/{solver.down_count()}")
                assert solver.up_count() == solver.count('up')
                assert solver.down_count() == solver.count('down')
                print()

if __name__ == '__main__':
    from logging import basicConfig, DEBUG, INFO
    basicConfig(level=INFO)
    main()
