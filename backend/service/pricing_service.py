

class Price:

    def __init__(self, fixed_rate=20):
        self.fixed_rate = 20

    def get_price(self, duration):
        '''
        Method to get price with a given duration input

        Input:
            duration: Numeric (float / int) representing how long does it take to wait in minutes

        Returns:
            price: Float: Price
        '''
        return self.fixed_rate * (duration / 60)
