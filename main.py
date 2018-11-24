import trdeg

if __name__ == '__main__':
    for (degree, rank) in zip(map(trdeg.Tenhou, [4, 5, 6, 7, 8]), [trdeg.TableRank.TOK]*3+[trdeg.TableRank.HOU]*2):
        for player in map(trdeg.ConstantEfficiencyArithmeticProgression, [5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5]):
            for kind in (trdeg.TableKind.HAN4, trdeg.TableKind.TON4):
                table = trdeg.Table(rank, kind)
                point = degree.point(table)
                solver = trdeg.Solver(
                        degree.index(point),
                        point,
                        player.probability(table))
                print('\t'.join(
                    map(str, [
                        degree, player, rank, kind, 
                        solver.up_prob(),
                        solver.up_count(),
                        solver.down_prob(),
                        solver.down_count()
                    ] + list(map(str, player.probability(table))))
                ))
