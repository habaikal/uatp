
import yfinance as yf

class LiquidityScanner:

    def scan(self,symbols):

        results=[]

        for s in symbols:

            data=yf.download(s,period="5d")

            volume=data["Volume"].mean()

            results.append((s,volume))

        return sorted(results,key=lambda x:x[1],reverse=True)
