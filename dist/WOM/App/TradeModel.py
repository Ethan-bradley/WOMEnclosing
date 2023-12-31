from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow
import plotly.graph_objects as go
import numpy as np
import matplotlib
from scipy.stats import norm
import statistics as stat
import plotly.express as px
import math

class Trade():
  def __init__(self, CountryListInput, CountryNameInput):
    self.CountryList = CountryListInput
    self.CountryName = CountryNameInput
    self.Tariffs = []
    self.Sanctions = []
    self.dead = []
    self.currencyReserves = []
    self.exchangeRates = []
    self.currencyChangeReserves = []
    self.total_flow = []
    self.exchangeRates = [1 for j in self.CountryList]
    self.equil_rate = 0
    self.restrictions = [{} for i in range(0,len(self.CountryList))]
    self.investment_restrictions = []
    self.balance = [0 for i in range(0,len(self.CountryList))]
    self.create_restriction_list(self.restrictions)
    self.foreign_investment = [[0 for j in range(0,len(self.CountryList))] for i in range(0,len(self.CountryList))]
    self.exchangeRateArr = [[] for j in self.CountryList]
    self.lastFlow = [None for i in range(len(self.CountryList[0].HouseProducts) + len(self.CountryList[0].CapitalGoods) + len(self.CountryList[0].RawGoods))]
    for i in self.CountryList:
      self.Tariffs.append([0.1 for j in self.CountryList])
      self.Sanctions.append([0 for j in self.CountryList])
      self.investment_restrictions = [0 for j in self.CountryList]
      self.currencyReserves.append([0 for j in self.CountryList])
      #self.exchangeRates.append([1 for j in self.CountryList])
      self.currencyChangeReserves = [[1 for j in self.CountryList] for i in self.CountryList]
  def create_restriction_list(self, restrictions):
    c = 0
    for dict in restrictions:
        dict['HouseProduction'] = [1 for i in range(0,len(self.CountryList[c].HouseProducts))]
        dict['CapitalProduction'] = [1 for i in range(0,len(self.CountryList[c].CapitalGoods))]
        dict['RawProduction'] = [1 for i in range(0,len(self.CountryList[c].RawGoods))]
        c += 1
        
  def add_restrictions(self, country_index, name, rest_list):
    self.restrictions[country_index][name] = rest_list

  def trade(self, Country, Tariffs, Sanctions):
    Sanctions = self.Sanctions
    self.Sanctions = Sanctions
    self.initial = True
    HousePriceArray = self.createHousePriceArray(Country)
    CapitalPriceArray = self.createCapitalPriceArray(Country)
    RawPriceArray = self.createRawPriceArray(Country)
    #print(HousePriceArray)
    #self.exchangeRates = [1 for j in self.CountryList]
    cheapest_house_prices = [min(i) for i in HousePriceArray]
    cheapest_capital_prices = [min(i) for i in CapitalPriceArray]
    cheapest_raw_prices = [min(i) for i in RawPriceArray]
    good_balance = [0 for i in range(0,len(Country))]
    trade_balance = [0 for i in range(0,len(Country))]
    Tariffs = self.Tariffs
    total_flow = [[[0 for j in range(0,len(Country))] for i in range(0,len(Country))] for i in range(0,2)]
    for i in range(0,len(self.exchangeRates)):
      if math.isnan(self.exchangeRates[i]):
        self.exchangeRates[i] = 1
    a = self.calculateTrade(Country, Tariffs, trade_balance, good_balance, 'HouseDemand','HouseProduction','HousePrices', cheapest_house_prices, total_flow, 0, 2)
    self.calculateTrade(Country, Tariffs, trade_balance, good_balance, 'CapitalDemand','CapitalProduction','CapitalPrices', cheapest_capital_prices, total_flow, 1, 3)
    self.calculateTrade(Country, Tariffs, trade_balance, good_balance, 'RawDemand','RawProduction', 'RawPrices', cheapest_raw_prices, total_flow, 3, 4)
    #Prints trade flow diagram
    equil_rate = 0
    total_gdp = 0
    global_price = 0
    for i in range(0,len(Country)):
      if not math.isnan(Country[i].GoodsTotal[len(Country[i].GoodsTotal) - 1]):
        equil_rate += Country[i].real_interest_rate*Country[i].GoodsTotal[len(Country[i].GoodsTotal) - 1]
        total_gdp += Country[i].GoodsTotal[len(Country[i].GoodsTotal) - 1]
        global_price += Country[i].ConsumerPrice*Country[i].GoodsTotal[len(Country[i].GoodsTotal) - 1]
    equil_rate = equil_rate / total_gdp
    global_price = global_price/ total_gdp
    self.equil_rate = equil_rate
    for i in range(0,len(Country)):
      price_index = (global_price/Country[i].ConsumerPrice)
      #new_rate = np.exp(((2*Country[i].interest_rate - Country[i].Inflation*0.01 - equil_rate)*price_index + ((trade_balance[i] + self.balance[i]*self.exchangeRates[i] + self.sum_cols(i, self.foreign_investment)*(self.CountryList[i].interest_rate)*self.exchangeRates[i])/Country[i].money[1])*price_index) + self.investment_restrictions[i])
      #new_rate = ((Country[i].interest_rate + 0.01*np.exp((trade_balance[i] + self.balance[i]*self.exchangeRates[i] - self.sum_cols(i, self.foreign_investment)*(self.CountryList[i].interest_rate)*self.exchangeRates[i] + self.sum_foreign_investment(i, self.foreign_investment))/Country[i].money[1]) - 0.01)/equil_rate)*price_index
      t = trade_balance[i] + self.balance[i]*self.exchangeRates[i] - self.sum_cols(i, self.foreign_investment)*(self.CountryList[i].interest_rate)*self.exchangeRates[i] + self.sum_foreign_investment(i, self.foreign_investment)
      #print("balance money", t)
      if (Country[i].money[1] < 0 or math.isnan(Country[i].money[1])):
        Country[i].money[1] = 20
      if (math.isnan(Country[i].real_interest_rate)):
        Country[i].real_interest_rate = 0.1

      savings_money_flow = 0.366*t - 8.333*(Country[i].real_interest_rate - equil_rate)+np.exp(-Country[i].money[1]*0.5)
      #savings_money_flow = 0.566*t - 8.333*(Country[i].real_interest_rate - equil_rate)+np.exp(-Country[i].money[1]*0.5)
      #print("savings money", savings_money_flow)
      new_rate = np.exp(-0.02*(savings_money_flow - t))

      print("new rates ", new_rate)
      if math.isnan(new_rate):
        new_rate = 1
      if math.isinf(new_rate):
        new_rate = 20
      if math.isnan(self.exchangeRates[i]):
        self.exchangeRates[i] = 1
      if abs(self.exchangeRates[i] - new_rate):
        t = trade_balance[i]
        new_rate = np.exp(-0.02*(savings_money_flow - t))
      if (new_rate/self.exchangeRates[i]) < 2 and (new_rate/self.exchangeRates[i]) > 0.5 and abs(self.exchangeRates[i] - new_rate) < 7:
        self.exchangeRates[i] = new_rate
      else:
        self.exchangeRates[i] = self.exchangeRates[i] + max(min((new_rate - self.exchangeRates[i])/100, self.exchangeRates[i]+7), self.exchangeRates[i]/10)
      self.exchangeRateArr[i].append(self.exchangeRates[i])
    #self.exchangeRates[0] - 0.07
    print("Exchange Rates ", self.exchangeRates)
    self.initial = False
    for i in range(0,len(self.exchangeRates)):
      if math.isnan(self.exchangeRates[i]):
        self.exchangeRates[i] = 1
    return self.second_trade(Country, Tariffs)
  
  def sum_cols(self, index, arr):
    total_sum = 0
    for i in range(0,len(arr)):
      total_sum += arr[i][index]
    return total_sum

  def sum_foreign_investment(self, index, arr):
    total_sum = 0
    for i in range(0,len(arr)):
      total_sum += arr[index][i]*self.CountryList[i].interest_rate*(self.exchangeRates[index]/self.exchangeRates[i])
    return total_sum

  def second_trade(self, Country, Tariffs):
    HousePriceArray = self.createHousePriceArray(Country)
    CapitalPriceArray = self.createCapitalPriceArray(Country)
    RawPriceArray = self.createRawPriceArray(Country)
    #print(HousePriceArray)
    cheapest_house_prices = [min(i) for i in HousePriceArray]
    cheapest_capital_prices = [min(i) for i in CapitalPriceArray]
    cheapest_raw_prices = [min(i) for i in RawPriceArray]
    good_balance = [0 for i in range(0,len(Country))]
    trade_balance = [0 for i in range(0,len(Country))]
    total_flow = [[[0 for j in range(0,len(Country))] for i in range(0,len(Country))] for i in range(0,2)]
    a = self.calculateTrade(Country, Tariffs, trade_balance, good_balance, 'HouseDemand','HouseProduction','HousePrices', cheapest_house_prices, total_flow, 0, 2)
    self.calculateTrade(Country, Tariffs, trade_balance, good_balance, 'CapitalDemand','CapitalProduction','CapitalPrices', cheapest_capital_prices, total_flow, 1, 3)
    self.calculateTrade(Country, Tariffs, trade_balance, good_balance, 'RawDemand','RawProduction', 'RawPrices', cheapest_raw_prices, total_flow, 3, 4)
    #Prints trade flow diagram
    for i in range(0,len(Country)):
      Country[i].tradeBalance = trade_balance[i]
    self.calculateForeignInvestment(trade_balance)
    print("Good Balance: ", good_balance)
    print("Trade Balanace: ", trade_balance)
    trade_diagram("trade", self.CountryName, total_flow[0], self.dead)
    return a
  
  def calculateForeignInvestment(self, trade_balance):
    surplus = [ele if ele > 0 else 0 for ele in trade_balance]
    deficit = [abs(ele) if ele < 0 else 0 for ele in trade_balance]
    total = sum(surplus)
    surplus = self.normalize(surplus)
    deficit = self.normalize(deficit)
    for i in range(0,len(self.CountryList)):
      for j in range(0,len(self.CountryList)):
        #i is the destination country, j is the source country.
        #am = self.foreign_investment[i][j]*(self.CountryList[j].interest_rate)*(self.exchangeRates[i]/self.exchangeRates[j])
        #self.CountryList[i].money[1] += am
        #self.CountryList[j].money[1] -= am
        self.foreign_investment[i][j] += surplus[i]*total*deficit[j]*self.exchangeRates[j]

  def normalize(self, arr):
    sum2 = sum(arr)
    if sum2 > 0:
      for i in range(0,len(arr)):
        arr[i] = arr[i]/sum2
    return arr

  def calculateTrade(self, Country, Tariffs, trade_balance, good_balance, demand_attr, supply_attr, price_attr, cheapest_prices, total_flow, goods_index, money_index):
    #if supply_attr == "RawProduction":
    #demand, supply, equil_price = self.findDemandSupplyRaw(Country, cheapest_prices, 2, 0, demand_attr, supply_attr)
    #else:
    demand, supply, equil_price = self.findDemandSupply(Country, cheapest_prices, money_index, goods_index, demand_attr, supply_attr)
    print(self.CountryName)
    print("Demand", demand)
    print("Supply", supply)
    for i in range(0,len(demand)):
      print("trade"+demand_attr+str(i))
      graph = self.create_graph(demand[i], supply[i], [0 for j in range(0,len(Country))], Tariffs, Country, price_attr, i, equil_price[i])
      #print(maximum_flow(csr_matrix(graph), 0, 1).flow_value)
      print("Max_flow result", maximum_flow(csr_matrix(graph), 0, 1).residual)
      flow2 = maximum_flow(csr_matrix(graph), 0, 1).residual
      #flows = maximum_flow(csr_matrix(graph), 0, 1).residual.data
      if not self.initial:
        lastFlow2 = self.lastFlow.pop(0)
      else:
        lastFlow2 = None
      if supply_attr == "RawProduction":
        parse_flows(lastFlow2, Country, good_balance, trade_balance, flow2, goods_index, money_index, equil_price[i], self.CountryName, self.initial, self.exchangeRates, i)
      else:
        parse_flows(lastFlow2, Country, good_balance, trade_balance, flow2, goods_index, money_index, equil_price[i], self.CountryName, self.initial, self.exchangeRates)
      get_flows(Country, flow2, equil_price[i], total_flow, Tariffs, i, price_attr, self.exchangeRates)
      if not self.initial:
        self.lastFlow.append(flow2)
      #print(demand_attr)
      trade_diagram("trade"+demand_attr+str(i),self.CountryName, total_flow[1], self.dead)

    self.total_flow = total_flow #print(total_flow)
    #trade_diagram(self.CountryName, total_flow)
    return flow2
  def createHousePriceArray(self, Country):
    price_array = []
    for j in range(0,len(Country[0].HousePrices)):
      price_array.append([])
      for i in range(0,len(Country)):
        price_array[j].append(Country[i].HousePrices[j]*self.exchangeRates[j])
    return price_array

  def createCapitalPriceArray(self, Country):
    price_array = []
    for j in range(0,len(Country[0].CapitalPrices)):
      price_array.append([])
      for i in range(0,len(Country)):
        price_array[j].append(Country[i].CapitalPrices[j]*self.exchangeRates[j])
    return price_array

  def createRawPriceArray(self, Country):
    price_array = []
    for j in range(0,len(Country[0].RawPrices)):
      price_array.append([])
      for i in range(0,len(Country)):
        price_array[j].append(Country[i].RawPrices[j]*self.exchangeRates[j])
    return price_array

  def findDemandSupply(self, Country, minimum_price, money_index, good_index, demand, supply):
    demand_array = []
    supply_array = []
    total_money = []
    equil_price = [0 for i in range(0,len(Country))]
    for i in range(0, len(minimum_price)):
      demand_array.append([])
      supply_array.append([])
      total_money.append([])
      for j in range(0,len(Country)):
        supply_array[i].append((Country[j].goods[good_index]*getattr(Country[j], supply)[i])*self.restrictions[j][supply][i]*100)
        if math.isnan(supply_array[i][j]):
          supply_array[i][j] = 1
      for j in range(0,len(Country)):
        total_money[i].append(Country[j].money[money_index]*getattr(Country[j], demand)[i]*self.exchangeRates[i])
      equil_price[i] = sum(total_money[i])/sum(supply_array[i])
      if math.isnan(equil_price[i]) or equil_price[i] == 0:
          equil_price[i] = 0.01
      for j in range(0,len(Country)):
        demand_array[i].append(((Country[j].money[money_index]*getattr(Country[j], demand)[i]*self.exchangeRates[i])/equil_price[i])*100)
        if math.isnan(demand_array[i][j]):
          demand_array[i][j] = 1
    #print("Total money: ", total_money)
    print("Equilibrium Price: ", equil_price)
    return demand_array, supply_array, equil_price
  
  def findDemandSupplyRaw(self, Country, minimum_price, money_index, good_index, demand, supply):
    demand_array = []
    supply_array = []
    total_money = []
    equil_price = [0 for i in range(0,len(Country))]
    for i in range(0, len(minimum_price)):
      demand_array.append([])
      supply_array.append([])
      total_money.append([])
      for j in range(0,len(Country)):
        supply_array[i].append((Country[j].raw_goods[i])*self.restrictions[j][supply][i])
        if math.isnan(supply_array[i][j]):
          supply_array[i][j] = 1
      for j in range(0,len(Country)):
        total_money[i].append(Country[j].money[money_index]*getattr(Country[j], demand)[i]*self.exchangeRates[i])
      equil_price[i] = sum(total_money[i])/sum(supply_array[i])
      if math.isnan(equil_price[i]) or equil_price[i] == 0:
          equil_price[i] = 0.01
      for j in range(0,len(Country)):
        demand_array[i].append((Country[j].money[money_index]*getattr(Country[j], demand)[i]*self.exchangeRates[i])/equil_price[i])
        if math.isnan(demand_array[i][j]):
          demand_array[i][j] = 1
    #print("Total money: ", total_money)
    print("Equilibrium Price: ", equil_price)
    return demand_array, supply_array, equil_price
  
  def create_graph(self,demand_list,supply_list,infrastructure, Tariffs, Country, attr, attr_index, equal_price):
    #graph = csr_matrix((len(), 4))
    supply_node = [0,0]
    inf = float('inf')
    countries = len(supply_list)
    for i in range(0,countries):
      supply_node.append(int(supply_list[i]))
    supply_node += [0 for i in range(0,countries)]
    infra = [[0 for i in range(0,countries*2 + 2)] for i in range(0,countries)]
    #print(len(infra))
    #print(len(infra[0]))
    #i is source country, j is destination country.
    for i in range(0,len(infra)):
      for j in range(countries + 2,countries*2 + 2):
        if (1 + Tariffs[j - countries - 2][i])*getattr(Country[i],attr)[attr_index] > equal_price or (1 + self.Sanctions[i][j - countries - 2])*getattr(Country[i],attr)[attr_index] > equal_price:
          infra[i][j] = 0
        elif j - countries - 2 == i:
          infra[i][j] = 214748364
        else:
          if math.isnan(Country[i].Infrastructure_Real):
            infra[i][j] = 10
          else:
            infra[i][j] = (int) (Country[i].Infrastructure_Real*4000000) #10000 # # #infrastructure[i]
    demand_nodes = [[0 for j in range(0,countries*2 + 2)] for i in range(0,countries)]
    for j in range(0,len(demand_nodes)):
      if math.isnan(demand_list[j]):
        demand_list[j] = 1
        demand_nodes[j][1] = int(demand_list[j])
      else:
        demand_nodes[j][1] = int(demand_list[j])
    demand_node = [0 for i in range(0,countries*2 + 2)]
    print("Demand Node", demand_nodes)
    matrix = [supply_node] + [demand_node] + infra + demand_nodes
    print("Matrix array:", matrix)
    #print(len(matrix))
    #print(len(matrix[0]))
    return matrix
  
  #Transfer money between countries. Transfer array is similar to tariff array, each row represnting the transfer wishes of one country
  def trade_money(self, Countries, transfer_array):
  #i is the destination country, j is the source country.
    for i in range(0, len(Countries)):
      for j in range(0, len(Countries)):
        am = transfer_array[j][i]*(self.exchangeRates[j]/self.exchangeRates[i])
        am2 = transfer_array[j][i]
        if (Countries[i].money[1]*0.25 < am):
          am = Countries[i].money[1]*0.25
          am2 = am*(self.exchangeRates[i]/self.exchangeRates[j])
        Countries[i].money[5] += am
        Countries[i].money[1] -= am
        self.balance[i] += am
        
        Countries[j].money[5] -= am2
        Countries[j].money[1] += am2
        self.balance[j] -= am

  #Transfer military goods between countries. Transfer array is similar to tariff array, each row represnting the transfer wishes of one country
  def trade_military_goods(self, Countries, transfer_array):
  #i is the destination country, j is the source country.
    for i in range(0, len(Countries)):
      for j in range(0, len(Countries)):
        am = transfer_array[j][i]
        am2 = transfer_array[j][i]
        if Countries[j].Military > am:
          Countries[i].Military += am
          Countries[j].Military -= am

def parse_flows(lastFlow, Countries, good_balance, trade_balance, flows, goods_index, money_index, price, country_names, initial, exchangeRates, raw_index=0):
  
  for i in range(0,len(Countries)):
    #Gets the flow value to/from that country of this particular good (getting the difference between the first and last arrows).
    flow = (flows[1, len(Countries) + 2 + i] + flows[0, i + 2])/100.0
    if flow == 0:
      flow = 1
    if math.isinf(exchangeRates[i]) or exchangeRates[i] > 30:
      exchangeRates[i] = 25
    #print(country_names[i],": ",flow)
    flow_percentage = 1
    if lastFlow != None:
      lastFlowTotal = lastFlow[1, len(Countries) + 2 + i] + lastFlow[0, i + 2]
      #flow = max(min(lastFlowTotal*1.01, flow), lastFlowTotal*0.99)
    good_balance[i] += flow*flow_percentage
    if math.isnan(price):
      price = 1
    value = flow*price*flow_percentage
    trade_balance[i] += value
    if not initial:
      if (Countries[i].money[1] - value*exchangeRates[i]) >= 0:
        if (Countries[i].money[money_index] + value*exchangeRates[i] >= 0):
          #if goods_index == 3:
          #  Countries[i].raw_goods[raw_index] -= flow*flow_percentage
          #  Countries[i].goods[goods_index] -= flow*flow_percentage
          #else:
          flow_am = flow*flow_percentage
          if abs(flow*flow_percentage) > Countries[i].goods[goods_index]*0.4:
            flow_am = Countries[i].goods[goods_index]*0.4*np.sign(flow_am)
          Countries[i].goods[goods_index] -= flow_am
          Countries[i].money[money_index] += value*exchangeRates[i]
          Countries[i].money[1] -= value*exchangeRates[i]
        elif (math.isnan(Countries[i].goods[goods_index])):
          Countries[i].goods[goods_index] = 1000
        elif (math.isnan(flow*flow_percentage*(Countries[i].money[1]/(value*exchangeRates[i])))):
          pass
        else:
          if goods_index == 3:
            Countries[i].raw_goods[raw_index] -= flow*flow_percentage*(Countries[i].money[1]/(value*exchangeRates[i]))
          Countries[i].goods[goods_index] -= flow*flow_percentage*(Countries[i].money[1]/(value*exchangeRates[i]))
          Countries[i].money[money_index] += Countries[i].money[1]
          Countries[i].money[1] = 5
      elif (math.isnan(Countries[i].money[1])):
          Countries[i].money[1] = 400
      elif (math.isnan(value)):
           value = 1
      elif (math.isnan(Countries[i].goods[goods_index])):
          Countries[i].goods[goods_index] = 100
      elif value*exchangeRates[i] != 0:
        #if math.isnan(Countries[i].money[1]/(value*exchangeRates[i])):
        #import pdb; pdb.set_trace();
        #if goods_index == 3:
        #Countries[i].raw_goods[raw_index] -= flow*flow_percentage*(Countries[i].money[1]/(value*exchangeRates[i]))
        Countries[i].goods[goods_index] -= flow*flow_percentage*(Countries[i].money[1]/(value*exchangeRates[i]))
        Countries[i].money[money_index] += Countries[i].money[1]
        Countries[i].money[1] = 200
  #trade_diagram(country_names, trade_balance)

def get_flows(Countries, flows, price, trade_flows, tarriffs, price_index, price_attr, exchangeRates):
  for i in range(2,len(Countries) + 2):
    for j in range(len(Countries) + 2, len(Countries)*2 + 2):
      value = flows[i, j]*price 
      #Tariff sent to j's government
      if value > 0:
        tarriff_am = value*tarriffs[j - len(Countries) - 2][i-2]*(1/exchangeRates[j - len(Countries) - 2])
        Countries[j - len(Countries) - 2].TariffRevenue += tarriff_am
        Countries[j - len(Countries) - 2].money[5] += tarriff_am
        Countries[j - len(Countries) - 2].money[1] -= tarriff_am
        #print("Tarriff", value*tarriffs[j - len(Countries) - 2][i-2])
      #Payment for infrastructure to country I's companies
      payment = (getattr(Countries[j - len(Countries) - 2], price_attr)[price_index]*exchangeRates[j - len(Countries) - 2] - price)*flows[i, j]*-1
      #print("Payment", payment)
      if payment > 0:
        Countries[i-2].TransportRevenue += payment
        Countries[i-2].money[4] += payment #*tarriffs[j - len(Countries) - 2][i-2]
        Countries[i-2].money[1] -= payment #*tarriffs[j - len(Countries) - 2][i-2]
      #Adding trade flow
      trade_flows[0][j - len(Countries) - 2][i - 2] += value
      trade_flows[1][j - len(Countries) - 2][i - 2] = value
  
def trade_diagram(name, CountryNames, tradeBalance, dead):
  new_trade_balance = []
  for i in range(0,len(tradeBalance)):
    for j in range(0,len(tradeBalance[i])):
      if i != j and (i not in dead) and (j not in dead):
        new_trade_balance.append(tradeBalance[i][j])
      else:
        new_trade_balance.append(0)
  print(new_trade_balance)
  #b.reverse()
  labels =  CountryNames*2
  #print([i for i in range(len(CountryNames),len(CountryNames)*2)] + [i for i in range(len(CountryNames)*2,len(CountryNames), -1)])
  data_trace = dict(
      type='sankey',
      domain = dict(
        x =  [0,1],
        y =  [0,1]
      ),
      orientation = "h",
      valueformat = ".0f",
      node = dict(
        pad = 10,
        thickness = 30,
        line = dict(
          color = "black",
          width = 0
        ),
        label = labels,
        color = create_color_array(len(CountryNames), 0.8, 2) #+ c  #['Red','Blue','Red','Blue']
      ),
      link = dict(
        source = [i for i in range(0,len(CountryNames))]*len(CountryNames), #+ [i for i in range(0,len(CountryNames))],
        target = [(int)(i/len(CountryNames)) + len(CountryNames)  for i in range(0, len(CountryNames)*len(CountryNames))],
        value = new_trade_balance,
        color = create_color_array(len(CountryNames), 0.4, len(CountryNames)) #['hsla(0, 100%, 50%, 0.4)','hsla(200, 100%, 50%, 0.4)','hsla(0, 100%, 50%, 0.4)','hsla(200, 100%, 50%, 0.4)'],
    )
  )

  layout =  dict(
      title = "Trade Flows",
      font = dict(
        size = 10
      ),
      height=750 
  )

  fig = go.Figure(dict(data=[data_trace], layout=layout))
  #go.iplot(fig, validate=False)
  #fig.show()
  fig.write_html("templates/App/"+name+".html")

def create_color_array(length, opacity, multiplier):
  arr = []
  for j in range(0,multiplier):
    for i in range(0,length):
      arr.append('hsla(' + str(i*25) + ', 100%, 50%, 0.4)')
  return arr

  