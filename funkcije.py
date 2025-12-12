import numpy as np
from scipy.stats import weibull_min
def monte_carlo_renewal_exponential(T, lambda_rate, N_simulations):
    counts = np.zeros(N_simulations)

    scale = 1 / lambda_rate 

    for i in range(N_simulations):
        t = 0.0
        c = 0

        while True:
            dt = np.random.exponential(scale=scale)
            if t + dt > T:
                break
            t += dt
            c += 1

        counts[i] = c

    return np.mean(counts)


def monte_carlo_renewal_weibull(T, beta_shape, alpha_scale, N_simulations):
    counts = np.zeros(N_simulations)

    for i in range(N_simulations):
        t = 0.0
        c = 0

        while True:
            dt = weibull_min.rvs(beta_shape, scale=alpha_scale)
            if t + dt > T:
                break
            t += dt
            c += 1

        counts[i] = c

    return np.mean(counts)


def monte_carlo_renewal_lognormal(T, mu, sigma, N_simulations):
    counts = np.zeros(N_simulations)

    for i in range(N_simulations):
        t = 0.0
        c = 0

        while True:
            dt = np.random.lognormal(mean=mu, sigma=sigma)
            if t + dt > T:
                break
            t += dt
            c += 1

        counts[i] = c

    return np.mean(counts)


def monte_carlo_time_to_k_failures(k, lambda0, N_sim=20000):
    total_times = np.zeros(N_sim)

    for sim in range(N_sim):
        lamb = lambda0
        time = 0

        for i in range(k):
            t = np.random.exponential(scale=1/lamb)
            time += t
            lamb /= 0.8

        total_times[sim] = time

    return np.mean(total_times)


def monte_carlo_time_to_k_failures_weibull(k, beta, eta0, degradation=0.8, N_sim=20000):
    times = np.zeros(N_sim)

    for sim in range(N_sim):
        eta = eta0
        t_total = 0.0
        for _ in range(k):
            u = np.random.rand()
            t = eta * (-np.log(1-u))**(1/beta)
            t_total += t
            eta *= degradation
        times[sim] = t_total

    return np.mean(times)

def monte_carlo_time_to_k_failures_lognormal(k, mu, sigma, degradation=0.8, N_sim=20000):
    times = np.zeros(N_sim)
    
    m0 = np.exp(mu + 0.5 * sigma**2)
    
    for sim in range(N_sim):
        t_total = 0.0
        
        for i in range(k):
            m_i = m0 * (degradation**i)  
            mu_i = np.log(m_i) - 0.5 * sigma**2
            t = np.random.lognormal(mean=mu_i, sigma=sigma)
            t_total += t
        
        times[sim] = t_total
        
    return np.mean(times)


