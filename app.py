from flask import Flask, jsonify, abort
from flask_cors import CORS, cross_origin

import os

from helper import *


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

port = os.getenv("PORT", 8070)

@app.route('/', methods=['Get'])
@cross_origin()
def index():
    return '<h1>You have made it</h1>'

@app.route('/gas', methods=['Get'])
@cross_origin()
def grabGasData():

    ethPrice = getEthPrice()
    gasPrices = getGasPrices()

    gasData = {
        'ethPrice': ethPrice,
        'fastGas': gasPrices['fastGas'],
        'proposedGas': gasPrices['proposedGas'],
        'safeGas': gasPrices['safeGas']
    }

    return jsonify(gasData)
    
@app.route('/wallet/<path:wallet>', methods=['Get'])
@cross_origin()
def grabData(wallet):
    if(not checkWallet(wallet)):
        abort(404)
    # tokenList = get721Tokens(wallet)
    gasData = getGasInfo(wallet)
    walletBalance = getBalance(wallet)
    # collectionData = testAgainstDB(tokenList)
    # erc20Tokens = getERC20Tokens(wallet)

    walletInfo = {
        'gasData' : gasData,
        'walletBalance' : walletBalance,
        # 'collectionData' : collectionData,
        # 'erc20Tokens': erc20Tokens
    }
    print(walletInfo)
    return jsonify(walletInfo)
    

@app.route('/txs/<path:wallet>', methods=['Get'])
@cross_origin()
def txBreakdown(wallet):
    return jsonify(getTxs(wallet))

if __name__ == '__main__':
    app.run(threaded=True, port = port)