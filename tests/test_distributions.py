from engine.distributions import NormalModel


def test_normal_over_prob_monotone():
    m = NormalModel(mu=100, sigma=15)
    assert m.over_prob(80) > m.over_prob(100) > m.over_prob(120)

