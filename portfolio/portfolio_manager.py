
import numpy as np

class PortfolioManager:

    def allocate(self,strategies):

        weights=np.random.dirichlet(np.ones(len(strategies)))

        return list(zip(strategies,weights))
