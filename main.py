import trdeg
import numpy
from numpy.linalg import solve

def solve_independent(player, kind):
    ret = {}
    for (dan, rank) in zip(
            [1, 2, 3,
            4, 5, 6,
            7, 8, 9, 10], [trdeg.TableRank.JOU] * 4 + [trdeg.TableRank.TOK] * 3 +[trdeg.TableRank.HOU] * 4):
        degree = trdeg.Tenhou(dan)
        table = trdeg.Table(rank, kind)
        point = degree.point(table)
        solver = trdeg.Solver(
                degree.index(point),
                point,
                player.probability(table))
        ret[dan] = (degree, rank, solver.solve())
    return ret

def expectation_JOU(independent_results):
    # calculate expectation of games played by the player during JOU
    table = trdeg.Table(trdeg.TableRank.JOU, kind)

    offset = 0

    matrix = numpy.identity(5)
    vector_games = numpy.zeros(5)

    for dan in range(1, 4):
        data = independent_results[dan][2]
        down_prob = data.down_prob
        up_prob = data.up_prob

        matrix[dan-offset, dan-offset-1] = -down_prob
        matrix[dan-offset, dan-offset+1] = -up_prob

        vector_games[dan-offset] = up_prob*data.up_count + down_prob*data.down_count

    # For 0-dan (1-kyu), use the following approximation:
    # up_prob = 1, down_prob=0, up_count=0, down_count=None
    matrix[0, 1] = -1
    vector_games[0-offset] = 0
    solution_games = solve(matrix, vector_games)
    return solution_games[3-offset]

def expectation_TOK(independent_results):
    offset = 3
    matrix = numpy.identity(5)
    vector_upprob = numpy.zeros(5)
    vector_dnprob = numpy.zeros(5)
    vector_upgames = numpy.zeros(5)
    vector_dngames = numpy.zeros(5)

    for dan in range(4, 7):
        data = independent_results[dan][2]
        down_prob = data.down_prob
        up_prob = data.up_prob

        matrix[dan-offset, dan-offset-1] = -down_prob
        matrix[dan-offset, dan-offset+1] = -up_prob

        vector_upgames[dan-offset] = up_prob*data.up_count
        vector_dngames[dan-offset] = down_prob*data.down_count

    vector_dnprob[3-offset] = 1
    vector_upprob[7-offset] = 1

    return (
            solve(matrix, vector_upprob)[6-offset],
            solve(matrix, vector_dnprob)[6-offset],
            solve(matrix, vector_upgames)[6-offset],
            solve(matrix, vector_dngames)[6-offset]
        )

def expectation_HOU(independent_results, kind):
    # calculate expectation of points gained and games played by the player during HOU
    table = trdeg.Table(trdeg.TableRank.HOU, kind)

    offset = 6

    matrix = numpy.identity(6)
    vector_points = numpy.zeros(6)
    vector_games = numpy.zeros(6)

    for dan in range(7, 11):
        data = independent_results[dan][2]
        down_prob = data.down_prob
        up_prob = data.up_prob

        matrix[dan-offset, dan-offset-1] = -down_prob
        matrix[dan-offset, dan-offset+1] = -up_prob

        vector_points[dan-offset] = (up_prob-down_prob) * dan*200
        vector_games[dan-offset] = up_prob*data.up_count + down_prob*data.down_count

    # For 11-dan (Tenhou-i), use the following approximation:
    # up_prob = 0, down_prob = 1, up_count = None, down_count = 2200/last
    matrix[11-offset, 10-offset] = -1
    vector_points[11-offset] = (0-1) * 11*200
    vector_games[11-offset] = 0*0 + 1*(11*200/trdeg.Tenhou(11).point(table)[4-1])

    solution_points = solve(matrix, vector_points)
    solution_games = solve(matrix, vector_games)

    return (solution_points[7-offset], solution_games[7-offset])

    # points (without correction):
    # E[6] = 0
    # E[7] = p(7>8)(E[8]+1400) + p(7>6)(E[6]-1400)
    # E[8] = p(8>9)(E[9]+1600) + p(8>7)(E[7]-1600)
    # :
    # E[10] = p(10>inf)(E[11] + 2000) + p(10>9)(E[9]-2000)
    # E[11] = 0 + 1(E[10]-2200)
    #
    #        E[6]                   = 0
    # -p(7>6)E[6] + E[7] -(7>8)E[8] = (p(7>8)-p(7>6))1400
    #
    # games:
    # E[6] = 0
    # E[7] = p(7>8)(E[7>8]+E[8]) + p(7>6)(E[7>6]+E[6])
    # E[8] = p(8>9)(E[8>9]+E[9]) + p(8>7)(E[8>7]+E[7])
    # :
    # E[10] = p(10>11)(E[10>11]+E[11]) + p(10>9)(E[10>9]+E[9])
    # E[11] = 0 + 1(approx+E[10])

def tsv(*tuples):
    buf = ''
    fsep = ''
    asep = '\t'
    for t in tuples:
        if not isinstance(t, tuple):
            buf += fsep + str(t)
        else:
            buf += fsep + asep.join(map(str, t))
        fsep = asep
    return buf


if __name__ == '__main__':
    print(tsv(
            'kind', 'player',
            'HOU-pt', 'HOU-gm',
            'TOK-u-p', 'TOK-d-p', 'TOK-u-g', 'TOK-d-g',
            'JOU-gm'))
    for kind in (trdeg.TableKind.HAN4, trdeg.TableKind.TON4):
        for player in map(trdeg.ConstantEfficiencyArithmeticProgression, [5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5]):
            independent_results = solve_independent(player, kind)
            print(tsv(
                    kind,
                    player,
                    expectation_HOU(independent_results, kind),
                    expectation_TOK(independent_results),
                    expectation_JOU(independent_results)))
