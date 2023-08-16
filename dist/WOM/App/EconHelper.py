import numpy as np
import matplotlib.pyplot as plt
import random
import copy
import matplotlib.cm as cm
import plotly.graph_objects as go
import plotly.express as px

def create_income_barchart(incomes, num_bins):
    # Create the histogram of income data
    _, bins, _ = plt.hist(incomes, bins=num_bins)
    
    # Set the labels and title
    plt.xlabel('Income')
    plt.ylabel('Count')
    plt.title('Income Distribution')
    
    # Display the bar chart
    plt.show()

#Run this cell
class Household():
  def __init__(self, goods_pref, reset_indexes, shares, endowments=None, labour_indexes=[2,3], education_index=3, kid_age=0):
    self.goods_pref = goods_pref
    self.goods_supply = [0 for i in range(len(goods_pref))]
    self.labour_indexes = labour_indexes
    self.reset_indexes = reset_indexes
    self.deposits = 0
    self.shares = shares
    self.loans = 0
    self.type2 = "Household"
    self.education_index = education_index
    self.members = {}
    self.member_names = []
    self.market = None
    self.num_children = 0
    self.num_workers = 0
    self.gov_education = 0
    self.kid_age = kid_age
    self.time_pref = 1 #Lower number means future consumption is preferred
    #self.random_list = [random.random() for _ in range(30)]
    #self.random_count = 0
    self.name_list = ['Bob','Henry','Juliet','Maria','John','Jack','List','Sophie','Mary','Ashley']
    
    if endowments == None:
      self.endowments = [1 for i in range(len(goods_pref))]
    else:
      self.endowments = endowments

  def setup_people(self):
    for i in range(0,2):
      self.add_population()
    self.add_population(False, self.kid_age)

  def utility(self):
    utility = 1
    for i in range(0,len(self.goods_supply)):
      utility *= pow(self.goods_supply[i], self.goods_pref[i])
    return utility
  
  def generate_name(self):
    #index = random.randrange(0,len(name_list))
    index = int(len(self.name_list) * random.random())
    #self.random_count = (self.random_count + 1) % len(self.random_list)
    return self.name_list[index]
  
  def generate_age(self):
    age =  21 + int(49 * random.random())#random.randrange(21,70)
    #self.random_count = (self.random_count + 1) % len(self.random_list)
    return age
    #return self.kid_age
  
  def setup_jobs(self):
    for i in range(len(self.member_names)):
      member = self.members[self.member_names[i]]
      #ipdb.set_trace()
      self.endowments[member[3]] += member[2]
    
  def run_turn(self, interest_rate, deposit_price, add_pop, real_interest, run_shares):
    for i in range(0,len(self.reset_indexes)):
      self.endowments[self.reset_indexes[i]] = 0
    for i in range(len(self.member_names)):
      member = self.members[self.member_names[i]]
      member[0] += 1
      #ipdb.set_trace()
      self.endowments[member[3]] += member[2]
    #self.endowments[self.labour_index] = 1
    #self.endowments[0] = self.goods_supply[0]
    if self.num_children > 0:
      self.determine_education()
    self.endowments[len(self.endowments)-1] = self.goods_supply[len(self.endowments)-1]
    self.deposits += (self.goods_supply[0]*deposit_price + self.deposits*interest_rate)
    if add_pop:
      self.add_population(False)
    if run_shares:
      self.determine_good_shares(real_interest)
  
  def determine_education(self):
    total_education = self.goods_supply[self.education_index]
    total_education /= self.num_children
    total_education += self.gov_education
    for i in range(0,len(self.member_names)):
      member = self.members[self.member_names[i]]
      if member[3] == 0:
        member[1] += total_education
        if member[0] > self.market.government.working_age:
          member[2] = 1
          self.graduate(member)
          self.num_children -= 1
          self.num_workers += 1
        elif member[0] > self.market.government.retirement_age:
          member[2] = 0
          self.num_workers -= 1
  
  def get_population(self):
    return len(self.member_names)

  def add_population(self, start=True, default_age=0):
    name = self.generate_name()
    #0st is age, 1nd is education level, 2rd is labour amount, 3th is labour index
    if start:
      age = self.generate_age()
    else:
      age = default_age
    self.members[name] = [age, 0, 0, 0]
    self.member_names.append(name)
    if age < 20:
      self.num_children += 1
    else:
      self.members[name][2] = 1
      self.members[name][3] = self.generate_weighted_random(self.labour_indexes[0], self.labour_indexes[-1], 3) 
      #random.randrange(self.labour_indexes[0],self.labour_indexes[-1])
      """if random.randrange(1,100) < 70:
        self.members[name][2] = 1
        self.members[name][3] = 2
      else:
        self.members[name][2] = 1
        self.members[name][3] = 3"""
      self.num_workers += 1

  def graduate(self, member):
    education_arr = self.market.manager.education_array
    prices = self.market.prices
    potential_jobs = []
    weights = []
    for i in range(len(education_arr)):
      if education_arr[i][1] <= member[1]:
        potential_jobs.append(education_arr[i][0])
    for i in range(len(potential_jobs)):
      weights.append(prices[potential_jobs[i]])
    job_index = self.choice(potential_jobs, weights)#random.choices(potential_jobs, weights=weights, k=1)[0]
    member[3] = job_index

  def determine_good_shares(self, interest_rate):
    amounts = []
    #loan_amount = 0
    saving_am = 1 - 1/(1 + 0.1*np.exp(interest_rate/self.time_pref))
    diff = (1-self.market.prices[0]) - self.market.interest_rate
    money_am = 1/(1 + np.exp(70*diff - 3))
    saving_pref = (1 - money_am)*saving_am
    money_pref = money_am*saving_am
    amounts.append(saving_pref)
    for i in range(1,len(self.goods_pref) - 1):
      amounts.append(self.shares[i]*(1-saving_am))
    amounts.append(money_pref)
    #self.loans += loan_amount
    #print(self.endowments[1])
    #amounts.append(sum(amounts)*0.1)
    total = sum(amounts)
    for i in range(0,len(self.goods_pref)):
        self.goods_pref[i] = amounts[i]/total

  def generate_random_list(self, start, end, length):
    random_list = []
    for _ in range(length):
        random_number = random.randint(start, end)
        random_list.append(random_number)
    return random_list
  
  def choice(self, options, probs):
    total = sum(probs)
    for j in range(0,len(probs)):
      probs[j] /= total
    x = np.random.rand()
    cum = 0
    for i,p in enumerate(probs):
        cum += p
        if x < cum:
            return options[i]

  def generate_weighted_random(self, start, end, bias_factor):
    # Calculate the range
    midpoint = (end - start)

    # Generate a random number following an exponential distribution
    random_num = random.expovariate(1 / bias_factor)

    # Map the random number to the desired range
    mapped_num = int(start + (random_num % midpoint))

    return mapped_num

"""## Corporation"""

class Corporation(Household):
  def __init__(self, goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes=[2], endowments=None, depreciation=0.05):
    super().__init__(goods_pref, reset_indexes, shares, endowments)
    #self.shares = shares #0 is capital, 1 is labour
    self.technology = tech
    self.output_good = output_good
    self.capital_indexes = capital_indexes
    self.labour_indexes = labour_indexes
    self.input_indexes = []
    self.type2 = "Corporation"
    self.loans = 0
    self.profit = 0
    self.taxprofit = 0
    self.revenue = 0
    self.expenses = 0
    self.wage_expense = 0
    self.depreciation = depreciation
    self.bankrupt = False
    self.connections = {"temp"}
    self.ResCap = 0.00000001
    self.researcher_index = 3
    self.TechArray = []
    self.FullBankrupt = False
    self.Resource = 0
    self.Resource_share = 0.2
    self.operating = False

  def production_function(self):
    output = self.technology
    for i in range(0,len(self.shares)):
      if self.shares[i] != 0:
        output *= pow(self.goods_supply[i], self.shares[i])
    if self.Resource != 0:
      output *= pow(self.Resource, self.Resource_share)
    return output
  #Price is the current price of the good this firm produces
  def calculate_capital_share(self, share, output, interest_rate, price):
    return share * (output/(interest_rate/price))

  def calculate_labour_share(self, share, output, wage, price):
    return share * (output/(wage/price))
  
  def calculate_tech_share(self, output, wage, price):
    #Change this
    tech_change = self.add_tech()
    return tech_change * (output/(wage/price))
  
  def add_tech(self):
    if self.output_good == 4:
      return 0
    connection_technology = 0
    for company in self.connections:
      connection_technology += company.technology
    own_research = 1*pow(self.ResCap, 0.7)*pow(self.goods_supply[self.researcher_index], 0.3)
    tech_change = pow(max(connection_technology - self.technology, 0), 0.7)*pow(own_research, 0.3)
    self.technology += tech_change
    return tech_change

  def determine_good_shares(self, output, interest_rate, price, wage, actual_interest_rate, prices):
    amounts = []
    #loan_amount = 0
    #ipdb.set_trace()
    for i in range(0,len(self.goods_pref)-1):
      if self.shares[i] != 0:
        if i in self.capital_indexes or i in self.input_indexes:
          tempc = self.calculate_capital_share(self.shares[i], output, prices[i]*actual_interest_rate, price)
          #loan_amount += tempc
          amounts.append(tempc)
        else:
          if i in self.labour_indexes:
            amounts.append(self.calculate_labour_share(self.shares[i], output, prices[i]*actual_interest_rate, price))
            if i == self.researcher_index:
              amounts[-1] += self.calculate_tech_share(output, prices[i]*actual_interest_rate, price) #self.calculate_labour_share(self.shares[i], output, prices[i]*actual_interest_rate, price)*0.3
          else:
            amounts.append(self.goods_pref[i])
      else:
        if self.researcher_index == 3:
          amounts.append(self.calculate_tech_share(output, prices[i]*actual_interest_rate, price))
        else:
          amounts.append(0)
    #self.loans += loan_amount
    #print(self.endowments[1])
    amounts.append(sum(amounts)*(0.005+actual_interest_rate*2)) #6
    total = sum(amounts)+0.0001
    for i in range(0,len(self.goods_pref)):
        self.goods_pref[i] = amounts[i]/total

  def calculate_balance_sheet(self, price, prices, wage):
    self.revenue = self.endowments[self.output_good]*price
    self.wage_expenses = sum([self.goods_supply[self.labour_indexes[i]]*prices[self.labour_indexes[i]] for i in range(0,len(self.labour_indexes))])
    self.expenses = self.wage_expenses + sum([(self.goods_supply[self.capital_indexes[i]] - self.endowments[self.capital_indexes[i]])*prices[self.capital_indexes[i]] for i in range(len(self.capital_indexes))])
    self.capital_expenses = sum([(self.goods_supply[self.capital_indexes[i]] - self.endowments[self.capital_indexes[i]])*prices[self.capital_indexes[i]] for i in range(len(self.capital_indexes))])
    self.input_expenses = sum([self.goods_supply[self.input_indexes[i]]*prices[self.input_indexes[i]] for i in range(0,len(self.input_indexes))])
    self.profit = self.revenue - self.expenses
    self.taxprofit = self.revenue - self.input_expenses - self.wage_expenses

  def run_bankruptcy(self, bank):
    bank.goods_supply[-1] += self.goods_supply[-1]
    bank.loans = max(bank.loans - self.loans, 0)
    self.FullBankrupt = True
  
  def run_restart_company(self):
    self.bankrupt = False
    self.FullBankrupt = False
    self.endowments[1] = 0
    self.goods_supply[-1] += 1
    self.loans = 0

  def run_turn(self, interest_rate, price, wage, run_shares, prices, actual_interest_rate, bank):
    self.calculate_balance_sheet(price, prices, wage)
    self.endowments[self.output_good] = self.production_function()
    if self.FullBankrupt:
      self.run_restart_company()
    if self.bankrupt:
      self.run_bankruptcy(bank)
      run_shares = True
    #Move this to else statement in run_shares if tech_share is implemented.
    #self.add_tech()
    if run_shares and not self.operating:
      self.determine_good_shares(self.endowments[self.output_good], interest_rate, price, wage*actual_interest_rate, actual_interest_rate, prices)
    else:
      self.add_tech()
    self.TechArray.append(self.technology)
    self.endowments[len(self.endowments)-1] = self.goods_supply[len(self.endowments)-1]
    interest = self.loans * actual_interest_rate
    if interest <= self.endowments[len(self.endowments)-1]:
      self.endowments[len(self.endowments)-1] -= interest
    else:
      #ipdb.set_trace()
      if not self.bankrupt:
        self.market.bankruptArr[-1] += 1
        print("Firm is bankrupt ", self.output_good)
        print(" $", self.loans, " of loans at risk.")
        self.bankrupt = True
      for i in range(0,len(self.goods_pref)-1):
        self.goods_pref[i] = 0.0
      self.goods_pref[-1] = 1.0
      #self.endowments[len(self.endowments)-1] = 0
    if self.profit < 0:
      self.endowments[1] = -self.profit
      self.loans -= self.profit
    if self.profit > 0:
      if self.loans < self.goods_supply[len(self.goods_supply)-1]:
        temp = self.loans
        bank.loans = max(bank.loans - temp,0)
        #Change this later to actually delete deposits
        bank.deposits = max(bank.deposits - temp,0)
        self.loans = 0
        self.goods_supply[len(self.goods_supply)-1] -= temp
      else:
        self.loans -= self.goods_supply[len(self.goods_supply)-1]
        bank.loans = max(bank.loans - self.goods_supply[len(self.goods_supply)-1], 0)
        #Change this later to actually delete deposits
        bank.deposits = max(bank.deposits - self.goods_supply[len(self.goods_supply)-1], 0)
        self.goods_supply[len(self.goods_supply)-1] = 0
      
    #print(self.endowments[1])
    for i in range(len(self.capital_indexes)):
      if self.capital_indexes[i] == self.output_good:
        self.endowments[self.capital_indexes[i]] += self.goods_supply[self.capital_indexes[i]]*(1-self.depreciation)
      else:
        self.endowments[self.capital_indexes[i]] = self.goods_supply[self.capital_indexes[i]]*(1-self.depreciation)

    #print(self.endowments[1])

"""## University"""

class University(Corporation):
  def __init__(self, goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes=[2], endowments=None, depreciation=0.05):
    super().__init__(goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, endowments)
    self.ResCap = 0.00000001
    self.type2 = "University"
    self.researcher_index = 3
    self.level = 1
  
  def add_tech(self):
    connection_technology = 0
    count = 0
    for company in self.connections:
      connection_technology += company.technology
      count += 1
    own_research = 1*pow(self.ResCap, 0.5)*pow(self.production_function(), 0.5)
    if count > 0:
      tech_change = pow(max(connection_technology - self.technology, 0), 0.4)*pow(own_research, 0.6)
    else:
      tech_change = own_research
    self.technology += tech_change
    return tech_change
  
  def calculate_balance_sheet(self, price, prices, wage):
    if self.revenue == 0:
      self.revenue = 1
    self.wage_expenses = sum([self.goods_supply[self.labour_indexes[i]]*prices[self.labour_indexes[i]] for i in range(0,len(self.labour_indexes))])
    self.expenses = self.wage_expenses + sum([(self.goods_supply[self.capital_indexes[i]] - self.endowments[self.capital_indexes[i]])*prices[self.capital_indexes[i]] for i in range(len(self.capital_indexes))])
    self.profit = self.revenue - self.expenses

  def determine_good_shares(self, output, interest_rate, price, wage, actual_interest_rate, prices):
    amounts = []
    #loan_amount = 0
    #ipdb.set_trace()
    for i in range(0,len(self.goods_pref) - 1):
      if self.shares[i] != 0:
        if i in self.capital_indexes:
          tempc = self.calculate_capital_share(self.shares[i], output, prices[i]*actual_interest_rate, price)
          #loan_amount += tempc
          amounts.append(tempc)
        else:
          if i in self.labour_indexes:
            amounts.append(self.calculate_labour_share(self.shares[i], output, prices[i]*actual_interest_rate, price))
          else:
            amounts.append(self.goods_pref[i])
      else:
        amounts.append(0)
    #self.loans += loan_amount
    #print(self.endowments[1])
    #amounts.append(sum(amounts)*(0.05+actual_interest_rate*3)) #6
    amounts.append(0)
    total = sum(amounts)+0.0001
    for i in range(0,len(self.goods_pref)):
        self.goods_pref[i] = amounts[i]/total

  def run_turn(self, interest_rate, price, wage, run_shares, prices, actual_interest_rate, bank):
    self.calculate_balance_sheet(price, prices, wage)
    tech_change = self.add_tech()
    self.TechArray.append(self.technology)
    #self.endowments[self.output_good] = self.production_function()
    if self.bankrupt:
      self.run_bankruptcy(bank)
    if run_shares:
      if tech_change != 0:
        p = self.endowments[-1]/tech_change
      else:
        p = 100
      self.determine_good_shares(tech_change, interest_rate, p, wage*actual_interest_rate, actual_interest_rate, prices)
    #pdb.set_trace()
    #self.endowments[len(self.endowments) - 1] = self.goods_supply[len(self.endowments) - 1]
    """interest = self.loans * actual_interest_rate
    if interest <= self.endowments[len(self.endowments) - 1]:
      self.endowments[len(self.endowments) - 1] -= interest
    else:
      #ipdb.set_trace()
      print("University is bankrupt ", self.output_good)
      print(" $", self.loans, " of loans at risk.")
      self.bankrupt = True
      for i in range(0,len(self.goods_pref)-1):
        self.goods_pref[i] = 0.0
      #self.endowments[len(self.endowments)-1] = 0
    if self.profit < 0:
      self.endowments[1] = -self.profit
      self.loans -= self.profit
    if self.profit > 0:
      if self.loans < self.goods_supply[len(self.goods_supply)-1]:
        temp = self.loans
        bank.loans = max(bank.loans - temp,0)
        #Change this later to actually delete deposits
        bank.deposits = max(bank.deposits - temp,0)
        self.loans = 0
        self.goods_supply[len(self.goods_supply)-1] -= temp
      else:
        self.loans -= self.goods_supply[len(self.goods_supply)-1]
        bank.loans = max(bank.loans - self.goods_supply[len(self.goods_supply)-1], 0)
        #Change this later to actually delete deposits
        bank.deposits = max(bank.deposits - self.goods_supply[len(self.goods_supply)-1], 0)
        self.goods_supply[len(self.goods_supply)-1] = 0
      
    #print(self.endowments[1])
    for i in range(len(self.capital_indexes)):
      self.endowments[self.capital_indexes[i]] = self.goods_supply[self.capital_indexes[i]]*(1-self.depreciation)

    #print(self.endowments[1])"""

"""## Trader"""

"""class Trader(Corporation):
  def __init__(self, goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, other_market, trade_manager, transportable_indexes, transport_index, endowments=None, sticky=0.1):
    super().__init__(goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, endowments)
    self.deposits = 1
    self.capital = 1
    self.new_capital = 1
    self.loans = 1
    self.type2 = "Trader"
    self.deposit_payments = 0
    self.other_market = other_market
    self.last_diff_array = []
    self.trade_manager = trade_manager
    self.transport_index = transport_index
    self.sticky = sticky
    self.other_trader = None

  def run_turn(self, prices):
    other_prices = self.other_market.prices
    labour_indexes = self.other_market.labour_indexes
    diff_array = []
    for i in range(2,len(prices)-1):
      if i in transportable_indexes:
        diff_array.append(max(other_prices[i] - prices[i] - prices[self.transport_index],0))
      else:
        diff_array.append(0)
    diff_array.append(0)
    if self.last_diff_array != []:
      transport_sum = 0
      for i in range(0,len(self.last_diff_array)-1):
        if i != self.transport_index-2:
          diff_array[i] = self.last_diff_array[i] + self.sticky*(diff_array[i] - self.last_diff_array[i])
          transport_sum += diff_array[i]
      diff_array[self.transport_index-2] = (transport_sum*0.5)
      self.normalize(diff_array)
    self.last_diff_array = diff_array
    #total_transport_ability = self.production_function()
    for i in range(2,len(self.goods_supply)):
      if i in transportable_indexes:
        self.other_trader.endowments[i] = self.goods_supply[i]
  
  def normalize(self, diff_array):
    #ipdb.set_trace()
    total = sum(diff_array)
    diff_array[len(diff_array)-1] = (total*0.1+0.01)
    total = sum(diff_array)
    for i in range(0,len(diff_array)):
      self.goods_pref[i+2] = diff_array[i]/total """
    
class Trader(Corporation):
  def __init__(self, goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, other_market, trade_manager, transportable_indexes, transport_index, endowments=None, sticky=0.1, currency_index=0, foreign_indexes=[]):
    super().__init__(goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, endowments)
    self.deposits = 1
    self.capital = 1
    self.new_capital = 1
    self.loans = 1
    self.type2 = "Trader"
    self.deposit_payments = 0
    self.other_market = other_market
    self.last_diff_array = []
    self.trade_manager = trade_manager
    #Index of transportation good
    self.transport_index = transport_index
    self.sticky = sticky
    #Index of the other currency
    self.currency_index = currency_index
    if self.currency_index == 0:
      self.currency_index = len(self.goods_pref)-1
    self.transportable_indexes = transportable_indexes
    self.foreign_indexes = foreign_indexes
    self.other_trader = None

  def run_turn(self, prices, market):
    other_prices = self.other_market.prices
    labour_indexes = self.other_market.labour_indexes
    self.currency_index = self.other_market.government.currency_index
    diff_array = []
    #ipdb.set_trace()
    for i in range(2,len(prices)-1):
      if i in self.transportable_indexes:
        tariff_am = self.endowments[i]*self.trade_manager.Tariffs[market.government.index][self.other_market.government.index]*prices[i]
        self.goods_supply[-1] = max(self.goods_supply[-1] - tariff_am, 0.01)
        market.government.TariffCollection += tariff_am
        #pdb.set_trace()
        tarriff_cost = (self.trade_manager.Tariffs[self.other_market.government.index][market.government.index] + self.trade_manager.good_tariffs[self.other_market.government.index][i])*other_prices[i]*prices[self.currency_index]
        sanction_cost = (self.trade_manager.Sanctions[market.government.index][self.other_market.government.index] + self.trade_manager.restrictions[market.government.index][i])*prices[i]
        #if i == 23 and self.type2 == "ForeignTrader" and market.turn > 5 and market.hexName == "Rome" and self.other_market.hexName == "Berlin": 
        #pdb.set_trace()
        diff_array.append(max(other_prices[i]*prices[self.currency_index] - prices[i] - prices[self.transport_index] - tarriff_cost - sanction_cost,0))
      elif i == market.government.currency_index and self.type2 == "ForeignTrader":
        diff_array.append(max(other_prices[i]*prices[self.currency_index] - 1,0))
      elif self.type2 == "ForeignTrader" and i in self.foreign_indexes:
        diff_array.append(max(other_prices[i]*prices[self.currency_index] - prices[i],0))
      else:
        diff_array.append(0)
    diff_array.append(0)
    diff_array[self.transport_index-2] = 0.1
    if self.last_diff_array != []:
      transport_sum = 0
      for i in range(0,len(self.last_diff_array)-1):
        if i in self.foreign_indexes:
          diff_array[i] = self.last_diff_array[i] + 0.95*(diff_array[i] - self.last_diff_array[i])
        if i != self.transport_index-2:
          #if diff_array[i] != 0.0:
          diff_array[i] = self.last_diff_array[i] + self.sticky*(diff_array[i] - self.last_diff_array[i])
          if i-2 in self.transportable_indexes and i-2 != self.transportable_indexes[-1]:
            transport_sum += diff_array[i]
      diff_array[self.transport_index-2] = (transport_sum*0.5)
      if market.turn < 3:
        new_am = transport_sum #*100 #0.25
      else:
        new_am = self.endowments[self.currency_index] + min(self.sticky*(transport_sum*4 -  self.endowments[self.currency_index]), 8*self.endowments[self.currency_index]+1)
      self.other_trader.endowments[1] = new_am
      self.loans += new_am
    self.normalize(diff_array, market)
    self.last_diff_array = diff_array
    #total_transport_ability = self.production_function()
    if self.type2 == "ForeignTrader":
      #ipdb.set_trace(context=6)
      for i in range(2,len(self.goods_supply)):
        if i in self.transportable_indexes:
          if i == self.transportable_indexes[-1]:
            self.other_trader.endowments[market.government.currency_index] = self.goods_supply[i]
          elif i == market.government.currency_index:
            pass
            #self.other_trader.endowments[-1] = self.goods_supply[i]
          else:
            #self.trade_manager.trade_balance[market.government.index][self.other_market.government.index] += self.goods_supply[i]
            self.trade_manager.trade_balance[self.other_market.government.index][market.government.index] += self.goods_supply[i]
            self.trade_manager.balance[self.other_market.government.index] -= self.goods_supply[i]
            self.trade_manager.good_balance[i][self.other_market.government.index][market.government.index] += self.goods_supply[i]
            self.trade_manager.balance[market.government.index] += self.goods_supply[i]
            #self.trade_manager.good_balance[market.government.index][market.government.index][i] -= self.goods_supply[i]
            self.other_trader.endowments[i] = self.goods_supply[i]
    else:
      for i in range(2,len(self.goods_supply)):
        if i in self.transportable_indexes:
          self.other_trader.endowments[i] = self.goods_supply[i]
  
  def normalize(self, diff_array, market):
    #ipdb.set_trace()
    total = sum(diff_array)
    if total == 0:
      diff_array[len(diff_array)-1] = 1
      return
    diff_array[len(diff_array)-1] = (total*0.1+0.01+diff_array[market.government.currency_index-2]/total)
    diff_array[market.government.currency_index-2] = 0
    total = sum(diff_array)
    for i in range(0,len(diff_array)):
      if i != market.government.currency_index-2:
        self.goods_pref[i+2] = diff_array[i]/total
      else:
        self.goods_pref[i+2] = 0
    #ipdb.set_trace()

"""## Bank"""

class Bank(Corporation):
  def __init__(self, goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, endowments=None, foreign_indexes=[], manager=None):
    super().__init__(goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, endowments)
    self.deposits = 1
    self.capital = 1
    self.new_capital = 1
    self.loans = 1
    self.type2 = "Bank"
    self.deposit_payments = 0
    self.foreign_indexes = foreign_indexes
    self.manager = manager
    self.bankrupt = False
  
  def calculate_balance_sheet(self, prices, wage, interest_rate, deposit_rate):
    self.revenue = self.loans*interest_rate
    self.wage_expenses = sum([self.goods_supply[self.labour_indexes[i]]*prices[self.labour_indexes[i]] for i in range(0,len(self.labour_indexes))])
    self.deposit_payments = self.deposits*deposit_rate
    self.expenses = self.wage_expenses + self.deposit_payments + sum([(self.goods_supply[self.capital_indexes[i]] - self.endowments[self.capital_indexes[i]])*prices[self.capital_indexes[i]] for i in range(len(self.capital_indexes))])
    self.profit = self.revenue - self.expenses
    self.new_capital += self.profit

  def run_bankruptcy(self, market):
    while (self.deposits > 0):
      house = market.get_random_household()
      house.deposits = max(house.deposits - 1, 0)
      self.deposits -= 1
    self.FullBankrupt = True

  def determine_good_shares(self, output, interest_rate, deposit_rate, wage, actual_interest_rate, prices, foreign_currencies, manager, market):
    amounts = []
    #loan_amount = 0
    #ipdb.set_trace()
    price = actual_interest_rate - deposit_rate
    for i in range(0,len(self.goods_pref)-1):
      if self.shares[i] != 0:
        if i in self.capital_indexes:
          tempc = self.calculate_capital_share(self.shares[i], output, prices[i]*interest_rate, price)
          #loan_amount += tempc
          amounts.append(tempc)
        elif i in self.foreign_indexes and i != market.government.currency_index:
          #ipdb.set_trace()
          tempc = self.calculate_capital_share(self.shares[i], max(self.endowments[i],1), prices[i]*interest_rate, max(manager.CountryList[foreign_currencies.index(i)].deposit_rate-deposit_rate,0.001))
          amounts.append(tempc)
        elif i == market.government.currency_index:
          amounts.append(0)
        else:
          if i in self.labour_indexes:
            amounts.append(self.calculate_labour_share(self.shares[i], output, prices[i]*actual_interest_rate, price))
          else:
            amounts.append(self.goods_pref[i])
      else:
        amounts.append(0)
    #self.loans += loan_amount
    #print(self.endowments[1])
    amounts.append(sum(amounts)*(0.01+actual_interest_rate*3)) #6
    total = sum(amounts)
    for i in range(0,len(self.goods_pref)):
        self.goods_pref[i] = amounts[i]/total
  def calculate_assets(self, prices):
    total = 0
    for i in range(0,len(self.endowments)):
        endown = self.endowments[i]
        if endown != 0:
          total += endown*prices[i]
    total += self.loans
    return total
  
  def run_turn(self, capital_cost, interest_rate, deposit_rate, wage, prices, run_shares, market):
    self.calculate_balance_sheet(prices, wage, interest_rate, deposit_rate)
    self.endowments[self.output_good] = self.production_function()
    if self.FullBankrupt == True:
      self.FullBankrupt = False
      self.bankrupt = False
      #pdb.set_trace()
    #Price should be interest rate on loans - interest rate on deposits
    if self.bankrupt:
      self.run_bankruptcy(market)
      return
    if run_shares:
      self.determine_good_shares(self.endowments[self.output_good], capital_cost, deposit_rate, wage*interest_rate, interest_rate, prices, self.foreign_indexes, self.manager, market)
    diff = self.loans*interest_rate - self.deposits*deposit_rate
    self.endowments[len(self.endowments)-1] = self.goods_supply[len(self.endowments)-1]
    diff = 0
    if diff < -self.endowments[len(self.endowments)-1]:
       self.endowments[len(self.endowments)-1] = 0
    else:
      self.endowments[len(self.endowments)-1] += diff
    self.loans += self.goods_supply[1]
    self.deposits += max(self.goods_supply[1] - self.new_capital, 0)
    self.new_capital = max(self.new_capital - self.goods_supply[1], 0)
    self.endowments[0] = self.goods_supply[1] + self.goods_supply[0]
    for i in range(len(self.capital_indexes)):
      if self.capital_indexes[i] == self.output_good:
        pass
        #self.endowments[self.capital_indexes[i]] += self.goods_supply[self.capital_indexes[i]]
      else:
        self.endowments[self.capital_indexes[i]] = self.goods_supply[self.capital_indexes[i]]
    for j in range(len(self.foreign_indexes)):
      lastAmount = self.endowments[self.foreign_indexes[j]]
      currAmount = self.goods_supply[self.foreign_indexes[j]]
      #self.manager.foreign_investment
      change = currAmount - lastAmount
      if change > 0:
        am = change*market.prices[self.foreign_indexes[j]]
        self.deposits += am
        self.endowments[0] += am
    if self.endowments[0] < 0:
      self.endowments[0] = 0
      
    if self.calculate_assets(prices) + 3 < self.deposits:
      print("Bank is bankrupt ", self.output_good)
      print(" $", self.deposits, " of deposits at risk.")
      self.bankrupt = True
      for i in range(0,len(self.goods_pref)-1):
        self.goods_pref[i] = 0.0

"""## Central Bank"""

class CentralBank(Bank):
  def __init__(self, goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, endowments=None):
    super().__init__(goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, endowments)
    self.type2= 'CentralBank'

  def run_turn(self, market):
    self.loans += self.goods_supply[1]
    self.deposits += self.goods_supply[0]
    self.endowments[0] = 0
    self.endowments[1] = 0
    self.endowments[len(market.prices)-1] = 0
    market.get_prices(1,1)
    market.get_prices(1,1)
    #if market.interest_rate - 1-market.get_prices(1,1) > 0:
    #if self.determine_loan_amount(market, 1) > 0:
    if market.interest_rate > 1 - market.get_prices(1,1):
      #Sell loans, increasing interest rate
      self.goods_pref[1] = 0
      self.goods_pref[len(self.goods_pref)-1] = 1
      #self.goods_pref[0] = 1
      amount = max(self.determine_loan_amount(market, 1), 0)
      self.endowments[1] = amount
      self.loans -= amount
    else:
      #Buy loans, decreasing interest rate
      self.goods_pref[len(self.goods_pref)-1] = 0
      #self.goods_pref[0] = 0
      self.goods_pref[1] = 1
      amount = max(self.determine_deposit_amount(market, 1),0)
      self.endowments[len(self.goods_pref)-1] = amount
      #self.endowments[0] = amount
      #self.deposits -= amount

  def determine_loan_amount(self, market, good_index):
    top = 0
    for j in range(0,len(market.goods_supply)):
      if j != good_index:
        middle = 0
        for i in range(0,len(market.households)):
          middle += market.households[i].goods_pref[good_index]*(market.households[i].endowments[j])
        top += middle*market.prices[j]
    bottom = 0
    for i in range(0,len(market.households)):
        if market.households[i] != self:
          bottom += (1-market.households[i].goods_pref[good_index])*(market.households[i].endowments[good_index])
    #if market.turn > 11:
    #ipdb.set_trace()
    amount = top/((1-market.interest_rate) - bottom)
    return amount
  
  def determine_deposit_amount(self, market, good_index):
    top = 0
    for j in range(0,len(market.goods_supply)):
      if j != good_index:
        middle = 0
        for i in range(0,len(market.households)):
          middle += market.households[i].goods_pref[good_index]*(market.households[i].endowments[j])
        top += middle*market.prices[j]
    bottom = 0
    for i in range(0,len(market.households)):
          bottom += (1-market.households[i].goods_pref[good_index])*(market.households[i].endowments[good_index])
    amount = (((1-market.interest_rate)*bottom) - top) #/market.prices[0]
    return amount

class CentralBank2(Bank):
  def __init__(self, goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, endowments=None):
    super().__init__(goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, endowments)
    self.type2= 'CentralBank'

  def run_turn(self, market):
    self.loans += self.goods_supply[1]
    self.deposits += self.goods_supply[0]
    self.endowments[0] = 0
    self.endowments[1] = 0
    self.endowments[len(market.prices)-1] = 0
    market.get_prices(0,1)
    market.get_prices(0,1)
    #if market.interest_rate - 1-market.get_prices(1,1) > 0:
    #if self.determine_loan_amount(market, 1) > 0:
    if market.deposit_rate > 1 - market.get_prices(0,1):
      #Sell deposits, increasing interest rate
      self.goods_pref[0] = 0
      self.goods_pref[len(self.goods_pref)-1] = 1
      #self.goods_pref[0] = 1
      amount = max(self.determine_loan_amount(market, 0), 0)
      self.endowments[0] = amount
      self.deposits -= amount
    else:
      #Buy Deposits, decreasing interest rate
      self.goods_pref[len(self.goods_pref)-1] = 0
      self.goods_pref[0] = 1
      #self.goods_pref[1] = 1
      amount = max(self.determine_deposit_amount(market, 0),0)
      self.endowments[len(self.goods_pref)-1] = amount
      #self.endowments[0] = amount
      #self.deposits -= amount

  def determine_loan_amount(self, market, good_index):
    top = 0
    for j in range(0,len(market.goods_supply)):
      if j != good_index:
        middle = 0
        for i in range(0,len(market.households)):
          middle += market.households[i].goods_pref[good_index]*(market.households[i].endowments[j])
        top += middle*market.prices[j]
    bottom = 0
    for i in range(0,len(market.households)):
        if market.households[i].type2 != self:
          bottom += (1-market.households[i].goods_pref[good_index])*(market.households[i].endowments[good_index])
    #if market.turn > 11:
    #ipdb.set_trace()
    amount = top/((1-market.deposit_rate) - bottom)
    return amount
  
  def determine_deposit_amount(self, market, good_index):
    top = 0
    for j in range(0,len(market.goods_supply)):
      if j != good_index:
        middle = 0
        for i in range(0,len(market.households)):
          middle += market.households[i].goods_pref[good_index]*(market.households[i].endowments[j])
        top += middle*market.prices[j]
    bottom = 0
    for i in range(0,len(market.households)):
          bottom += (1-market.households[i].goods_pref[good_index])*(market.households[i].endowments[good_index])
    amount = (((1-market.deposit_rate)*bottom) - top) #/market.prices[0]
    return amount

"""## Government"""

class Government(Household):
  def __init__(self, goods_pref, reset_indexes, good_names, endowments=None, education_index=4):
    super().__init__(goods_pref, reset_indexes, [], endowments)
    self.spending = [0 for i in range(0,len(goods_pref))]
    self.IncomeTax = 0.05
    self.CorporateTax = 0.0
    self.GovWelfare = 0.0
    self.ResearchSpend = 0.005
    self.Government_Savings = 0
    self.good_names = good_names
    self.deficit = 0
    self.GovName = ""
    self.type2 = "Government"
    self.welfare_threshold = 100
    self.interest_rate = 0.1
    self.deposit_rate = 0.07
    self.currency_index = 0
    self.education_index = education_index
    self.index = 0
    self.TaxCollector = None
    self.retirement_age = 70
    self.working_age = 20
    self.TariffCollection = 0
    self.Education = 0
    self.num_children = 1
    self.ResAm = 0
    self.InfrastructureInvest = 0.0
    self.Military = 0
    self.time = 0
    self.subsidies = [0 for i in range(0,len(goods_pref))]
    self.price_history = [[] for i in range(0,len(self.goods_pref))]
    self.supply_history = [[] for i in range(0,len(self.goods_pref))]
    self.labour_indexes = None
    self.markets = []

    #Arrays
    self.IncomeTaxArray = [0]
    self.CorporateTaxArray = [0]
    self.GovWelfareArray = [0]
    self.EducationArray = [0]
    self.ScienceBudgetArr = [0]
    self.MilitaryArr = [0]
    self.Government_SavingsArray = [0]
    self.deficits = [0]
    self.TarriffCollectionArray = [0]
    self.InfrastructureArr = [0]
    self.SubsidyArr = [0]
    self.GDPGrowth = [0]

    #Indexes
    #pdb.set_trace()
    self.EducationIndex = good_names.index('Education')
    self.MilitaryIndex = good_names.index('Military')
    self.InfrastructureIndex = good_names.index('Construction')
    self.TransportIndex = good_names.index('Transport')

    self.spending[self.EducationIndex] = 0.01
    self.spending[self.MilitaryIndex] = 0.01

    self.GDPPerCapita = []
    self.InterestRate = []

    #Indicators
    self.var_list = ['GDP','UnemploymentArr','InfrastructureArray','PopulationArr', 'CapitalArr', 'CapitalPerPerson', 'InflationTracker', 'ResentmentArr','Happiness', 'EmploymentRate','ConsumptionArr2', 'Bankruptcies', 'gini', 'EducationArr2','Iron','Crops','Coal','Oil','Food','Services','Steel','Machinery','IronP','WheatP','CoalP','OilP','FoodP','ConsumerGoodsP','SteelP','MachineryP','Income_Tax','Corporate_Tax']
    self.variable_list = ['output','unemployment','InfrastructureArray','population', 'CapitalArr', 'CapitalPerPerson', 'inflation',      'Resentment','happiness', 'employment', 'ConsumptionArr2', 'bankruptArr', 'gini', 'EducationArr2','#Iron','#Crops','#Coal','#Oil','#Food','#Services','#Steel','#Machinery','@Iron','@Crops','@Coal','@Oil','@Food','@Services','@Steel','@Machinery','!IncomeTax','!CorporateTax']
    self.weight = [     'N',      'PopulationArr','N',                    'N',         'N',           'PopulationArr',  'GDP',     'PopulationArr'  ,'PopulationArr','PopulationArr',   'PopulationArr', 'N',         'PopulationArr', 'PopulationArr', 'N','N'] +['N' for i in range(0,7)] +['GDP' for i in range(0,7)]+['N','N']
    self.weight_dict = {'PopulationArr':'population', 'GDP':'output'}
    self.index_array = []
    self.save_variable_list(self.var_list)

  def save_variable_list(self, var_list):
    for i in range(0,len(var_list)):
      setattr(self,var_list[i],[])
      if self.variable_list[i][0] == "#" or self.variable_list[i][0] == "@":
        self.index_array.append(self.good_names.index(self.variable_list[i][1:]))
      else:
        self.index_array.append(0)
  
  def append_variable_list(self):
    for i in range(0,len(self.var_list)):
      if self.variable_list[i][0] == "!":
        getattr(self,self.var_list[i]).append(getattr(self,self.variable_list[i][1:]))
      else:
        getattr(self,self.var_list[i]).append(0)
    for i in range(0,len(self.goods_pref)):
      self.price_history[i].append(0)
      self.supply_history[i].append(0)
  
  def add_variable_list(self, M):
    weight2 = 1
    for i in range(0,len(self.var_list)):
      weight2 = 1
      if self.variable_list[i][0] == "!":
        continue
      if self.weight[i] != 'N':
        weight2 = getattr(M, self.weight_dict[self.weight[i]])[-1]
      if self.variable_list[i][0] == "#":
        getattr(self,self.var_list[i])[-1] += M.supply_history[self.index_array[i]][-1]*weight2
      elif self.variable_list[i][0] == "@":
        getattr(self,self.var_list[i])[-1] += M.prices[self.index_array[i]]*weight2
      else:
        getattr(self,self.var_list[i])[-1] += getattr(M, self.variable_list[i])[-1]*weight2
    for j in range(0,len(M.prices)-1):
      self.price_history[j][-1] += (M.price_history[j][-1])*M.output[-1]
      self.supply_history[j][-1] += (M.supply_history[j][-1])*M.output[-1]
  
  def normalize_variable_list(self):
    for i in range(0,len(self.var_list)):
      if self.weight[i] != 'N':
        getattr(self, self.var_list[i])[-1] /= getattr(self, self.weight[i])[-1]
    for i in range(0,len(self.goods_pref)-1):
        self.price_history[i][-1] /= self.GDP[-1]
        self.supply_history[i][-1] /= self.GDP[-1]

  def get_market_data():
    pass

  def run_turn(self, interest_rate, deposit_price, gdp):
    self.total_spending = min(sum(self.spending),1)
    self.normalize()
    spending = self.total_spending*gdp
    self.subsidies[self.TransportIndex] = (self.InfrastructureInvest*gdp)/2
    self.EducationArray[-1] += (self.spending[self.EducationIndex]*gdp)
    self.MilitaryArr[-1] += (self.spending[self.MilitaryIndex]*gdp)
    self.InfrastructureArr[-1] += (self.spending[self.InfrastructureIndex]*gdp)
    self.Military += self.goods_supply[self.MilitaryIndex]
    
    self.Government_Savings -= spending
    self.endowments[len(self.endowments)-1] = spending
    deficit = -spending + self.TariffCollection
    self.Education = self.goods_supply[self.education_index] / self.num_children
    self.num_children = 1
    self.ResAm = self.ResearchSpend*gdp
    deficit -= self.ResAm
    self.ScienceBudgetArr[-1] += (self.ResAm)
  
  def record_data(self):
    self.Government_SavingsArray.append(self.Government_Savings)
    self.deficits.append(self.deficit)
    self.IncomeTaxArray.append(0)
    self.CorporateTaxArray.append(0)
    self.GovWelfareArray.append(0)
    self.deficit = 0
    self.EducationArray.append(0)
    self.MilitaryArr.append(0)
    self.InfrastructureArr.append(0)
    self.ScienceBudgetArr.append(0)
    self.SubsidyArr.append(0)
    self.InterestRate.append(self.interest_rate)
    self.TarriffCollectionArray.append(self.TariffCollection)
    self.TariffCollection = 0
    if self.PopulationArr[-1] != 0:
      self.GDPPerCapita.append(self.GDP[-1]/self.PopulationArr[-1])
    else:
      self.GDPPerCapita.append(1)
    if len(self.GDP) > 1:
      self.GDPGrowth.append((self.GDP[-1]/self.GDP[-2]-1)*100)
    self.time += 1

  def normalize(self):
    for i in range(0,len(self.spending)):
      self.goods_pref[i] = self.spending[i]/self.total_spending
  
  def display_graphs(self, start_year):
    for i in self.var_list:
      plt.title(i)
      plt.plot(getattr(self, i)[start_year:], label=i)
      plt.ylabel(i)
      plt.xlabel('Years')
      plt.legend()
      plt.show()


class TaxCollector(Household):
  def __init__(self, goods_pref, reset_indexes, government, endowments=None):
    super().__init__(goods_pref, reset_indexes, [], endowments)
    self.spending = [0 for i in range(0,len(goods_pref))]
    self.IncomeTax = 0.0
    self.CorporateTax = 0.0
    self.Government = government
    self.goods_pref[len(self.goods_pref)-1] = 1
    self.type2 = "TaxCollector"

  def run_turn(self, M):
    self.IncomeTax = self.Government.IncomeTax
    self.CorporateTax = self.Government.CorporateTax
    self.Government.Government_Savings += self.goods_supply[len(self.goods_supply)-1]
    self.Government.deficit += self.goods_supply[len(self.goods_supply)-1]
    self.Government.IncomeTaxArray[-1] += self.goods_supply[len(self.goods_supply)-1]
    for i in range(0,len(M.labour_indexes)):
      self.endowments[M.labour_indexes[i]] = 0
    self.collect_tax(M)
    self.gov_banking(M)

  def gov_banking(self, M):
    if self.Government.Government_Savings < 0:
      if self.Government.deficit < 0:
        self.endowments[1] -= self.Government.deficit
        self.loans -= self.Government.deficit
      else:
        for i in range(0,10):
          bank = M.get_random_bank()
          am = max(bank.loans - self.Government.deficit*0.1,0)
          bank.loans = am
          self.loans -= am
          #Change this later to actually delete deposits
          bank.deposits = max(bank.deposits - self.Government.deficit*0.1,0)
    else:
      self.Government.Government_Savings *= M.deposit_rate
      #Could add government buying deposits here though it doesn't matter too much

  def collect_tax(self, M):
    labour_indexes = M.labour_indexes
    for j in range(0,len(M.households)):
      if M.households[j].type2 == "Household":
        for i in labour_indexes:
          #Collect Income Tax by taking labour endowment
          if M.households[j].endowments[i] > 0:
            M.households[j].endowments[i] = (1 - self.IncomeTax)*M.households[j].endowments[i]
            self.endowments[i] += self.IncomeTax*M.households[j].endowments[i]
        M.households[j].gov_education = self.Government.Education
        #Distribute welfare
        #if M.prices[M.households[j].labour_index] < self.Government.welfare_threshold:
        self.Government.GovWelfareArray[-1] += self.Government.GovWelfare
        M.households[j].endowments[-1] += self.Government.GovWelfare
        self.Government.deficit -= self.Government.GovWelfare
        self.Government.Government_Savings -= self.Government.GovWelfare
      #Collect Corporate Tax
      elif M.households[j].type2 == "Corporation":
        amount = max(M.households[j].taxprofit,0)*self.CorporateTax
        subsidy = self.Government.subsidies[M.households[j].output_good]
        M.households[j].endowments[-1] = max(M.households[j].endowments[-1] - amount, 0) + subsidy
        self.Government.CorporateTaxArray[-1] += amount
        amount += subsidy
        self.Government.Government_Savings += amount
        self.Government.deficit += amount
        self.Government.SubsidyArr[-1] += subsidy
      elif M.households[j].type2 == "Bank":
        amount = max(M.households[j].profit,0)*self.CorporateTax
        M.households[j].new_capital = max(M.households[j].new_capital - amount, 0)
        self.Government.CorporateTaxArray[-1] += amount
        self.Government.Government_Savings += amount
        self.Government.deficit += amount
      elif M.households[j].type2 == "University":
        am = self.Government.ResAm * (M.households[j].level/M.universityLevel)
        M.households[j].endowments[-1] += am
        M.households[j].revenue = am

"""## Market"""

class Market():
  def __init__(self, goods_supply, goods_names, central_bank_index, labour_indexes, final_goods, households=None, traders=None):
    self.goods_supply = goods_supply
    self.prices = [1 for i in range(0,len(goods_supply))]
    self.prices[1] = 0.9
    self.prices[0] = 0.95
    self.goods_names = goods_names
    if households == None:
      self.households = [Household([0.3,0.4,0.3]), Household([0.3,0.4,0.3])]
    else:
      self.households = households
    self.price_history = [[] for i in range(0,len(self.prices))]
    self.supply_history = [[] for i in range(0,len(self.prices))]
    self.output = []
    self.output_per_capita = []
    self.population = []
    self.workers = []
    self.InfrastructureArray = []
    self.happiness = []
    self.cpi = []
    self.unemployment = []
    self.employment = []
    self.ConsumptionArr2 = []
    self.inflation = [0]
    self.output_growth = [0]
    self.final_goods = final_goods
    self.turn = 0
    self.gini = []
    self.EducationArr2 = []
    self.CapitalArr = []
    self.CapitalPerPerson = []
    self.Resentment = [0]
    self.interest_rate = 0.1
    self.deposit_rate = 0.05
    self.depreciation = 0.05
    self.central_bank_index = central_bank_index
    self.sticky = 0.3 #Lower value means prices are more sticky, a higher value up to 1.
    self.labour_sticky = 0.5
    self.inflation_expectation = 0.02
    self.CBBalanceSheet = [0]
    self.labour_indexes = labour_indexes
    self.government = self.households[len(self.households)-2]
    self.bank_indexes = []
    self.household_indexes = []
    self.traders = traders
    self.hexName = ""
    self.manager = None
    self.runNum = 6#4
    self.universityLevel = 0
    self.bankruptArr = []
    self.add = 15
    for i in range(0,len(self.households)):
      self.households[i].market = self
      if self.households[i].type2 == "Bank":
        self.bank_indexes.append(i)
      if self.households[i].type2 == "Household":
        self.households[i].setup_people()
        self.household_indexes.append(i)

  def get_prices(self, good_index, sticky):
    #if good_index == 0 or good_index == 4:
    #ipdb.set_trace()
    top = 0
    for j in range(0,len(self.goods_supply)):
      if j != good_index:
        middle = 0
        for i in range(0,len(self.households)):
          middle += self.households[i].goods_pref[good_index]*(self.households[i].endowments[j])
        top += middle*self.prices[j]
    bottom = 0
    for i in range(0,len(self.households)):
        bottom += (1-self.households[i].goods_pref[good_index])*(self.households[i].endowments[good_index])
    if bottom == 0:
      self.prices[good_index] = 1
    elif good_index > 1:
      new_price = top/bottom
      self.prices[good_index] = min(self.prices[good_index] + sticky*(new_price - self.prices[good_index]), self.prices[good_index]*15)
    else:
      self.prices[good_index] = top/bottom
    if top == 0:
      print("Error with this price: ", good_index)
    return self.prices[good_index]
  
  def get_amounts(self, household_index, good_index):
    #print(good_index)
    self.households[household_index].goods_supply[good_index] = (self.households[household_index].goods_pref[good_index]/self.prices[good_index])*(sum([(self.households[household_index].endowments[i])*self.prices[i] for i in range(0,len(self.goods_supply))]))
    return self.households[household_index].goods_supply[good_index]
  
  def run_market(self, iterations, new_goods_supply=None):
    if new_goods_supply != None:
      self.goods_supply = new_goods_supply
    #price_random = random.sample(range(0, len(self.prices)-1), (int)(len(self.prices)/2))
    for k in range(0,iterations):
      self.interest_rate = self.government.interest_rate
      self.deposit_rate = self.government.deposit_rate
      self.households[self.central_bank_index].run_turn(self)
      self.households[self.central_bank_index+1].run_turn(self)
      self.households[self.central_bank_index].run_turn(self)
      self.households[self.central_bank_index+1].run_turn(self)
      self.CBBalanceSheet.append(self.households[self.central_bank_index].loans)
      self.get_prices(1,1)
      self.get_prices(0,1)
      self.bankruptArr.append(0)
      self.InfrastructureArray.append(0)
      self.EducationArr2.append(0)
      #if 1-self.prices[1] != self.interest_rate:
      #self.prices[1] = 1 - self.interest_rate
      for i in range(0,len(self.prices)-1):#-1
        #if random.randrange(0,3) == 1 and i > 1:
        #self.get_prices(i)
        if i > 1 and (not self.manager or not i in self.manager.currency_indexes):
          if i in self.labour_indexes:
            self.get_prices(i, self.labour_sticky)
          else:
            self.get_prices(i, self.sticky)
        self.price_history[i].append(self.prices[i])
      #self.interest_rate = 1-self.prices[1]+1e-10
      #self.deposit_rate = 1-self.prices[0]+1e-10
      #self.prices[1] = 1-self.interest_rate
      #self.prices[0] = 1 #-self.deposit_rate
      temp_output = 0
      temp_nominal = 0
      for i in range(0,len(self.supply_history)):
        self.supply_history[i].append(0)
      for i in range(0,len(self.households)):
        for j in range(0,len(self.goods_supply)):
          self.supply_history[j][self.turn] += self.households[i].endowments[j]
          if j != self.government.currency_index:
            self.get_amounts(i,j)
          #temp_cpi = *self.prices[j]
      #if self.turn > 20:
      #ipdb.set_trace(context=6)
      #self.unemployment.append(self.households[0].goods_supply[2])
      household_random = random.sample(range(0, len(self.households)), (int)(len(self.households)/self.runNum))
      #ipdb.set_trace()
      if len(self.population) > 0:
        add_pop_indexes = random.sample(self.household_indexes, max((int)(self.population[-1]/40),1))
      else:
        add_pop_indexes = []
      household_num = 0
      labour_used = 0
      num_workers = 0
      num_children = 0
      num_population = 0
      happy = 0
      self.ConsumptionArr2.append(0)
      for i in range(0,len(self.households)):
        if self.households[i].type2 == "Household":
          self.households[i].run_turn(self.deposit_rate, self.prices[0], i in add_pop_indexes, self.deposit_rate-self.inflation_expectation, i in household_random)
          household_num += self.households[i].get_population()
          num_workers += self.households[i].num_workers
          num_children += self.households[i].num_children
          num_population += self.households[i].get_population()
          happy += self.households[i].utility()
          self.EducationArr2[-1] += self.households[i].gov_education
        elif self.households[i].type2 == "Corporation":
          if self.households[i].output_good > 1:
            for j in self.labour_indexes:
              labour_used += self.households[i].goods_supply[j]
            production = self.households[i].production_function()
            if i in self.households[0].reset_indexes:
              self.ConsumptionArr2[-1] += temp_output
            if self.goods_names[self.households[i].output_good] in self.final_goods:
              temp_output += production
              temp_nominal += production*self.prices[self.households[i].output_good]
          self.households[i].run_turn(interest_rate=(self.interest_rate-self.inflation_expectation)*(1-self.depreciation), price=self.prices[self.households[i].output_good], wage=self.prices[2], run_shares=(i in household_random), prices=self.prices, actual_interest_rate=self.interest_rate, bank=self.get_random_bank())
        elif self.households[i].type2 == "University":
          for j in self.labour_indexes:
              labour_used += self.households[i].goods_supply[j]
          self.households[i].run_turn(interest_rate=(self.interest_rate-self.inflation_expectation)*(1-self.depreciation), price=self.prices[self.households[i].output_good], wage=self.prices[2], run_shares=(i in household_random), prices=self.prices, actual_interest_rate=self.interest_rate, bank=self.get_random_bank())
        elif self.households[i].type2 == "Bank":
          #if self.turn > 20:
          #ipdb.set_trace(context=6)
          for j in self.labour_indexes:
            labour_used += self.households[i].goods_supply[j]
          self.households[i].run_turn((self.interest_rate-self.inflation_expectation)*(1-self.depreciation), self.interest_rate, self.deposit_rate, self.prices[2],self.prices,(i in household_random), self)
        elif self.households[i].type2 == "Government":
          self.government.num_children += num_children
          self.households[i].run_turn(self.interest_rate, self.deposit_rate, temp_nominal)
          self.government.num_children = 1
        elif self.households[i].type2 == "TaxCollector":
           self.households[i].run_turn(self)
        elif self.households[i].type2 == 'Trader' or self.households[i].type2 == 'ForeignTrader':
          self.households[i].run_turn(self.prices, self)
          self.InfrastructureArray[-1] += sum([self.households[i].goods_supply[j] for j in self.households[i].capital_indexes])
      #if self.turn > 20:
      #ipdb.set_trace(context=6)
      #self.unemployment.append(max((1-(labour_used/num_workers)), 0.005)*100)
      self.gini.append(self.gini_coefficient())
      self.add = 18
      unemployment2 = (1-(labour_used/num_workers))*100+self.add
      unemployment2 = max(0.5,unemployment2)
      #if unemployment2 < -30:
      #self.add = 80
      self.unemployment.append(unemployment2)
      self.employment.append(((labour_used/household_num))*100 - self.add)
      self.population.append(num_population)
      self.workers.append(num_workers)
      self.happiness.append(happy/len(self.household_indexes))
      temp_cpi = temp_nominal/temp_output
      self.ConsumptionArr2[-1] /= household_num
      self.output.append(temp_nominal/temp_cpi)
      self.output_per_capita.append(self.output[-1]/household_num)
      self.cpi.append(temp_cpi)
      self.CapitalArr.append(sum([self.supply_history[j][-1] for j in self.traders[0].capital_indexes]))
      self.CapitalPerPerson.append(self.CapitalArr[-1]/household_num)
      self.EducationArr2[-1] /= household_num
      if len(self.cpi) > 1:
        self.inflation.append(((self.cpi[self.turn]-self.cpi[self.turn-1])/self.cpi[self.turn-1])*100)
        self.output_growth.append(((self.output[self.turn]-self.output[self.turn-1])/self.output[self.turn-1])*100)
        happy_change = max(((self.happiness[-1]/self.happiness[-2]) - 1)*100,0)
        self.Resentment.append(pow(abs(self.inflation[-1]), 0.1)*pow(happy_change + 100, -0.5)*pow(self.unemployment[-1], 0.4)*0.4)
      if len(self.inflation) > 8:
        self.inflation_expectation = (sum(self.inflation[-4:])/400)
      if self.interest_rate - self.inflation_expectation <= 0:
        self.inflation_expectation = self.interest_rate-0.01
      #self.inflation_expectation = 0
      self.government.add_variable_list(self)
      self.turn += 1

  def get_random_bank(self):
    return self.households[self.bank_indexes[random.randint(0,len(self.bank_indexes)-1)]]
  
  def get_random_household(self):
    return self.households[self.bank_indexes[random.randint(0,len(self.bank_indexes)-1)]]

  def display_prices(self):
    for i in range(0,len(self.prices)):
      print(self.goods_names[i]+": ","$"+str(self.prices[i]))
  
  def display_goods(self, household_num):
    for i in range(0,len(self.prices)):
      print(self.goods_names[i]+": ",str(self.households[household_num].goods_supply[i]))
  
  def balance_sheet(self, corporate_num):
    string = "Output good: "+self.goods_names[self.households[corporate_num].output_good]+" \n"
    string += "Assets: \n"
    total = 0
    if self.households[corporate_num].type2 == "Corporation":
      for i in range(0,len(self.households[corporate_num].endowments)):
        endown = self.households[corporate_num].endowments[i]
        if endown != 0:
          total += endown*self.prices[i]
          string += ("  "+self.goods_names[i]+": $"+str(endown*self.prices[i]))+" \n"
      string += ("Total: $"+str(total)+" \n")
      string += "Liabilities: \n"
      string += ("  Loans: $"+str(self.households[corporate_num].loans) + " \n")
      string += ("Revenue: $"+str(self.households[corporate_num].revenue) +" \n")
      string += ("Subsidies: $"+str(self.government.subsidies[corporate_num]) +" \n")
      string += ("Expenses: $"+str(self.households[corporate_num].expenses) +" \n")
      string += ("  Wage Expenses: $"+str(self.households[corporate_num].wage_expenses) +" \n")
      string += ("  Input Expenses: $"+str(self.households[corporate_num].input_expenses) +" \n")
      string += ("  Capital Expenditures: $"+str(self.households[corporate_num].capital_expenses) +" \n")
      string += ("Operating Profit: $"+str(self.households[corporate_num].taxprofit) +" \n")
      string += ("Profit: $"+str(self.households[corporate_num].profit) +" \n")
      print(string)
    elif self.households[corporate_num].type2 == "Bank" or self.households[corporate_num].type2 == "CentralBank":
      for i in range(0,len(self.households[corporate_num].endowments)):
        endown = self.households[corporate_num].endowments[i]
        if endown != 0:
          total += endown*self.prices[i]
          string += ("  "+self.goods_names[i]+": $"+str(endown*self.prices[i]))+" \n"
      total += self.households[corporate_num].loans
      string += ("  Loans: $"+str(self.households[corporate_num].loans) + " \n")
      string += ("Total: $"+str(total)+" \n")
      string += "Liabilities: \n"
      string += ("  Deposits: $"+str(self.households[corporate_num].deposits) + " \n")
      string += ("Capital: $"+str(total - self.households[corporate_num].deposits) + "\n")
      string += ("Revenue: $"+str(self.households[corporate_num].revenue) +" \n")
      string += ("Expenses: $"+str(self.households[corporate_num].expenses) +" \n")
      string += ("  Wage Expenses: $"+str(self.households[corporate_num].wage_expenses) +" \n")
      string += ("  Deposit Payments: $"+str(self.households[corporate_num].deposit_payments) +" \n")
      string += ("Profit: $"+str(self.households[corporate_num].profit) +" \n")
      print(string)
  
  def display_price_history(self, start_year):
    plt.title('Prices')
    for i in range(1,len(self.prices)):
      plt.plot(self.price_history[i][start_year:], label=self.goods_names[i])
    plt.ylabel('Price')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('Supply')
    for i in range(1,len(self.prices)):
      plt.plot(self.supply_history[i][start_year:], label=self.goods_names[i])
    plt.ylabel('Supply')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

  def get_income_list(self):
    x = []
    for house in self.households:
      for i in self.labour_indexes:
        for j in range(0,int(house.endowments[i]/(1-self.government.IncomeTax))):
          x.append(house.endowments[i]*self.prices[i])
    return x

  def gini_coefficient(self, x=None):
    """Compute Gini coefficient of array of values"""
    if x == None:
      x = self.get_income_list()
    x = np.array(x)
    diffsum = 0
    for i, xi in enumerate(x[:-1], 1):
        diffsum += np.sum(np.abs(xi - x[i:]))
    return diffsum / (len(x)**2 * np.mean(x))
  
  def create_income_barchart(incomes, num_bins):
    # Create the histogram of income data
    _, bins, _ = plt.hist(incomes, bins=num_bins)
  
    # Set the labels and title
    plt.xlabel('Income')
    plt.ylabel('Count')
    plt.title('Income Distribution')
    
    # Display the bar chart
    plt.show()

  def display_graphs(self, start_year):
    plt.title('Output')
    plt.plot(self.output[start_year:], label="Output")
    plt.ylabel('Output')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('GDP per Capita')
    plt.plot(self.output_per_capita[start_year:], label="GDP per Capita")
    plt.ylabel('GDP per Capita')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('GDP Deflator')
    plt.plot(self.cpi[start_year:], label="GDP Deflator")
    plt.ylabel('GDP Deflator')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('GDP Growth')
    plt.plot(self.output_growth[start_year:], label="GDP Growth")
    plt.ylabel('GDP Growth')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('Inflation')
    plt.plot(self.inflation[start_year:], label="Inflation")
    plt.ylabel('Inflation')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('Inequality')
    plt.plot(self.gini[start_year:], label="Inequality")
    plt.ylabel('Gini Coefficent')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    incomes = self.get_income_list()
    create_income_barchart(incomes, 5)

    plt.title('Population')
    plt.plot(self.population[start_year:], label="Population")
    plt.ylabel('Population')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('Happiness')
    plt.plot(self.happiness[start_year:], label="Happiness")
    plt.ylabel('Happiness')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('Workers')
    plt.plot(self.workers[start_year:], label="Workers")
    plt.ylabel('Workers')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('Unemployment')
    plt.plot(self.unemployment[start_year:], label="Unemployment")
    plt.ylabel('Unemployment Rate')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('Employment')
    plt.plot(self.employment[start_year:], label="Employment")
    plt.ylabel('Employment Rate')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('Capital Per Person')
    plt.plot(self.CapitalPerPerson[start_year:], label="CapitalPerPerson")
    plt.ylabel('Capital Per Person')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('Central Bank Balance Sheet')
    plt.plot(self.CBBalanceSheet[start_year:], label="Loans")
    plt.ylabel('Loans')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('Bankruptcies')
    plt.plot(self.bankruptArr[start_year:], label="Bankruptcies")
    plt.ylabel('Bankruptcies')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    plt.title('Government Deficit')
    plt.plot(self.government.deficits[start_year:], label="Deficit")
    plt.ylabel('Deficit')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    colors = cm.get_cmap('nipy_spectral', len(self.goods_names)*10)

    plt.title('Technology')
    for i in range(0,len(self.households)):
      if self.households[i].type2 == "Corporation" or self.households[i].type2 == "University":
        plt.plot(self.households[i].TechArray[start_year:], label=self.goods_names[self.households[i].output_good], color=colors(self.households[i].output_good*10))
    plt.ylabel('Tech Level')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

original_list = ['Clothes', 'Services', 'Housing', 'Healthcare', 'Military', 'MedicalEquipment', 'Steel', 'Crops', 'Iron', 'Coal']
bracketed_list = [[item] for item in original_list]

universitySetup = [['Food'],['Education'],['Clothes'],['Services'],['Housing'],['Construction'],['Healthcare'],['Military'],['MedicalEquipment'],['Steel'],['Crops'],['Iron'],
 ['Coal'],['Oil'], ['Transport'], ['Machinery'], ['Deposits'],['Physics'],['Biology'],['Chemistry']]
universityConnectSetup = [['Biology','Chemistry'],[],['Chemistry'],[],['Physics'],['Physics'],['Biology'],['Chemistry','Physics'],['Biology'], ['Chemistry','Physics'],['Biology'],['Chemistry','Physics'],['Chemistry','Physics'],['Chemistry','Physics'],[],['Chemistry','Physics'], [],[], ['Chemistry'],['Physics']]

"""## Creation Manager"""

#Good 0 is Deposits, Good 1 is Loans, [Labour types], [Consumer Goods], [Capital Goods], [Raw Goods], [Intermediate Goods]
class CreationManager():
  def __init__(self, goods, goods_type, good_industry, num_households, num_corp_per_industry, industry_dict, final_goods, hex, researcher_indexes,transportable_indexes=[], manager=None, foreign_currencies=[], government_created=False):
    self.households = []
    self.goods = goods
    self.hex = hex
    self.government = None
    self.manager = manager
    self.universitySetup = [['Food'],['Education'],['Clothes'],['Services'],['Housing'],['Construction'],['Healthcare'],['Military'],['MedicalEquipment'],['Steel'],['Crops'],['Iron'],
 ['Coal'],['Oil'], ['Transport'], ['Machinery'], ['Deposits'],['Physics'],['Biology'],['Chemistry']]
    self.universityConnectSetup = [['Biology','Chemistry'],[],['Chemistry'],[],['Physics'],['Physics'],['Biology'],['Chemistry','Physics'],['Biology'], ['Chemistry','Physics'],['Biology'],['Chemistry','Physics'],['Chemistry','Physics'],['Chemistry','Physics'],[],['Chemistry','Physics'], [],[], ['Chemistry'],['Physics']]
    self.techDict = {}
    self.resourceLink = {'Iron':0, 'Crops':1, 'Coal':2, 'Oil':3}
    self.researcher_indexes = researcher_indexes
    age_diff = 20 / num_households
    kid_age = 0
    Household_pref = []
    consum_goods = goods_type.count('Consumer')
    labour_types = goods_type.count('Labour')
    endowments = [0 for i in range(len(goods))]
    transportable_indexes = transportable_indexes
    transport_index = 5
    reset_indexes = []
    for i in range(len(goods)):
      if goods_type[i] == 'Consumer':
        Household_pref.append(1.0/consum_goods)
        if i > 1:
          reset_indexes.append(i)
      elif goods_type[i] == 'Transport':
        transport_index = i
        Household_pref.append(0)
      else:
        Household_pref.append(0)
    capital_index = []
    labour_index = []
    input_indexes = []
    for i in range(0, len(goods) - 1):
      if goods_type[i] == 'Capital':
        capital_index.append(i)
      elif goods_type[i] == 'Raw':
        input_indexes.append(i)
      elif goods_type[i] == 'Labour':
        labour_index.append(i)
    reset_indexes += labour_index
    for i in range(num_households):
      #labour_index_count = 2 + random.randrange(0,labour_types)
      #endowments[labour_index_count] = 1
      endowments[len(goods)-1] = random.randrange(1,6)
      self.households.append(Household(copy.deepcopy(Household_pref),reset_indexes,copy.deepcopy(Household_pref),endowments=copy.deepcopy(endowments), labour_indexes=labour_index, education_index=goods.index('Education'), kid_age=(int)(kid_age)))
      self.households[-1].setup_jobs()
      kid_age += age_diff
    corporations = []
    corporations.append(CentralBank([0 for i in range(0,len(goods))], [], 1, [0 for i in range(0,len(goods))], i, [], [],endowments=[0 for i in range(0,len(goods))]))
    corporations.append(CentralBank2([0 for i in range(0,len(goods))], [], 1, [0 for i in range(0,len(goods))], i, [], [],endowments=[0 for i in range(0,len(goods))]))
    #University steup
    curr_index = len(corporations)
    for i in range(0, len(self.universitySetup)):
      shares = industry_dict['Chemistry']
      goods_pref = [(shares[j]) / 2 for j in range(0,len(goods))]
      goods_pref[len(goods_pref)-1] = 0.5
      endowments[1] = 0
      for j in range(2,labour_types+2):
        endowments[j] = 0
      endowments[len(endowments)-1] = 1
      university = University(copy.deepcopy(goods_pref),[],1,shares,i,capital_index, labour_index, endowments=copy.deepcopy(endowments))
      corporations.append(university)
      for j in range(0, len(self.universitySetup[i])):
        self.techDict[self.universitySetup[i][j]] = university
    for i in range(0, len(self.universityConnectSetup)):
      for j in range(0, len(self.universityConnectSetup[i])):
        #pdb.set_trace()
        corporations[curr_index+i].connections.add(self.techDict[self.universityConnectSetup[i][j]])
      corporations[curr_index+i].connections.remove("temp")
    for i in range(0, len(goods)-1):
      if goods_type[i] == 'Labour':
        continue
      if i == 1 or goods_type[i] == 'ForeignCurrency':
        continue
      shares = industry_dict[good_industry[i]]
      goods_pref = [(shares[j]/sum(shares)) / 2 for j in range(0,len(goods))]
      goods_pref[len(goods_pref)-1] = 0.5
      endowments = [0 for k in range(0,len(goods))]
      endowments[1] = 1
      endowments = [1 if goods_type[j] == 'Capital' else 0 for j in range(len(goods))]
      endowments[i] = 1
      endowments[len(endowments)-1] = 1
      tempSet = {"temp"}
      #Add university type corporation to tempSet
      tempSet.add(self.techDict[goods[i]])
      for j in range(0,num_corp_per_industry[i]):
        if goods_type[i] == 'Deposits' or i == 0:
          endowments[0] = 2
          corporations.append(Bank(copy.deepcopy(goods_pref),[],1,shares,i,capital_index, labour_index, endowments=copy.deepcopy(endowments),foreign_indexes=foreign_currencies, manager=self.manager))
        elif goods_type[i] != 'ForeignCurrency':
          corp = Corporation(copy.deepcopy(goods_pref),[],1,shares,i,capital_index, labour_index, endowments=copy.deepcopy(endowments))
          corp.input_indexes = input_indexes
          corp.researcher_index = self.researcher_indexes[good_industry[i]]
          #Adds in resources
          if goods_type[i] == "Raw":
            corp.Resource = hex[6+self.resourceLink[self.goods[i]]]+0.0000000000001
            corp.Resource_share = 0.2
          tempSet.add(corp)
          corporations.append(corp)
      tempSet.remove("temp")
      for corp in tempSet:
        corp.connections = tempSet
    trader_array = []
    #self, goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, other_market, trade_manager, endowments=None, sticky=0.1
    goods_pref = [0,0] + [1/(len(goods)-2) for i in range(2,len(goods))]
    endowments = [0 for k in range(0,len(goods))]
    endowments[len(endowments)-1] = 1
    if self.manager != None:
      for i in range(0,len(self.manager.location_names)-1):
        trader = Trader(copy.deepcopy(goods_pref),[],1,shares,i, capital_index, labour_index, None, manager, transportable_indexes, transport_index, endowments=copy.deepcopy(endowments), sticky=manager.sticky, foreign_indexes=foreign_currencies)
        corporations.append(trader)
        trader_array.append(trader)
    if government_created == None:
      gov_goods_pref = [0 for i in range(0,len(goods))]
      gov_goods_pref[len(goods)-1] = 1
      self.government = Government(gov_goods_pref,[],self.goods, [0.0 for i in range(0,len(goods))], goods.index('Education'))
      self.government.labour_indexes = labour_index
      corporations.append(self.government)
      tax = TaxCollector([0 for i in range(0,len(goods))], [], self.government,[0.0 for i in range(0,len(goods))])
      corporations.append(tax)
      self.government.TaxCollector = tax
    else:
      self.government = government_created
      corporations.append(government_created)
      corporations.append(government_created.TaxCollector)
    self.households = self.households + corporations
    self.market = Market([2 for i in range(0,len(goods))], goods, num_households, labour_index, final_goods, households=self.households, traders=trader_array)
    self.market.universityLevel = len(self.universitySetup)

  def get_market(self):
    return self.market
  
  def get_government(self):
    return self.government

"""## Manager"""

#from ast import NameConstant
def create_industry_dict(good_names, goods_type, industry_types, industry_value_dict):
  industry_dict = {}
  researcher_indexes = {}
  #labour_types = goods_type.count('Labour')
  for i in range(0, len(industry_types) -1):
    if (i >= len(goods_type)) or (goods_type[i] != 'Labour' and goods_type[i] != 'ForeignCurrency'):
      industry_dict[industry_types[i]] = [0 for i in range(0,len(good_names))]
      for j in range(len(industry_value_dict[industry_types[i]])):
        index = good_names.index(industry_value_dict[industry_types[i]][j][0])
        industry_dict[industry_types[i]][index] = industry_value_dict[industry_types[i]][j][1]
      researcher_indexes[industry_types[i]] = good_names.index(industry_value_dict[industry_types[i]][-1][0])

  return researcher_indexes, industry_dict
#self, goods_pref, reset_indexes, tech, shares, output_good, capital_indexes, labour_indexes, other_market, trade_manager, endowments=None, sticky=0.1
class Manager():
  def __init__(self, hex_array, good_names, good_types, industry_types, num_households, num_corp_per_industry, industry_dict, CountryList, transportable_indexes, education_array, final_goods, researcher_indexes):
    self.market_list = []
    self.market_dict = {}
    self.Tariffs = []
    self.Sanctions = []
    self.hex_list = hex_array
    self.CountryList = CountryList
    self.CountryNameList = CountryList
    self.good_names = good_names
    self.currNames = []
    self.balance = [0 for i in range(0,len(self.CountryList))]
    self.trade_balance_history = [[] for i in range(0,len(self.CountryList))]
    self.trade_balance = [[0 for i in range(0,len(self.CountryList))] for i in range(0,len(self.CountryList))]
    self.good_balance = [[[0 for k in range(0,len(self.CountryList))] for j in range(0,len(self.CountryList))] for i in range(0, len(good_types))]
    #self.good_balance_history = [[[] for i in range(0, len(good_types))] for i in range(0,len(self.CountryList))]
    self.foreign_investment = [[0 for j in range(0,len(self.CountryList))] for i in range(0,len(self.CountryList))]
    self.exchangeRateArr = [[1] for j in self.CountryList]
    self.restrictions = [[0 for j in range(0,len(self.good_names))] for i in range(0,len(self.CountryList))]
    self.good_tariffs = [[0 for j in range(0,len(self.good_names))] for i in range(0,len(self.CountryList))]
    self.location_names = []
    self.education_array = education_array
    for i in range(0,len(self.hex_list)):
      for j in range(0,len(self.hex_list[i])):
        if not self.hex_list[i][j][1]:
          self.location_names.append(self.hex_list[i][j][0])
    self.currency_indexes = [i for i in range(len(good_names)-1-len(CountryList), len(good_names)-1)]
    self.sticky = 0.1#0.6/len(self.location_names)
    for i in self.CountryList:
      self.Tariffs.append([0.1 for j in self.CountryList])
      self.Sanctions.append([0 for j in self.CountryList])
      self.investment_restrictions = [0 for j in self.CountryList]
    self.CountryList = []
    for i in range(0,len(hex_array)):
      for j in range(0,len(hex_array[i])):
        #Create only if hex is not an ocean
        if not hex_array[i][j][1]:
          if hex_array[i][j][2] == 75:
            num_corp_per_industry = [3 for i in range(len(good_names))]
            num_households = 45#int(hex_array[i][j][2]/3)
          elif hex_array[i][j][2] == 100:
            num_corp_per_industry = [4 for i in range(len(good_names))]
            num_households = 60#int(hex_array[i][j][2]/3)
          else:
            num_corp_per_industry = [2 for i in range(len(good_names))]
            num_households = 30#int(hex_array[i][j][2]/3)
          if not hex_array[i][j][4] in self.currNames:
            CM = CreationManager(good_names, good_types, industry_types, num_households, num_corp_per_industry, industry_dict, final_goods, self.hex_list[i][j], researcher_indexes, transportable_indexes, self, foreign_currencies=self.currency_indexes, government_created=None)
            country_name = hex_array[i][j][4]
            gov = CM.get_government()
            gov.GovName = country_name
            self.CountryList.append(gov)
            self.currNames.append(country_name)
            self.CountryList[-1].currency_index = self.currency_indexes[self.CountryNameList.index(country_name)] #Fixed. i*len(hex_array[i])+j
            self.CountryList[-1].index = len(self.CountryList) - 1
          else:
            CM = CreationManager(good_names, good_types, industry_types, num_households, num_corp_per_industry, industry_dict, final_goods, self.hex_list[i][j], researcher_indexes, transportable_indexes, self, foreign_currencies=self.currency_indexes, government_created=self.CountryList[self.currNames.index(hex_array[i][j][4])])
          M = CM.market
          self.CountryList[self.currNames.index(hex_array[i][j][4])].markets.append(M)
          M.manager = self
          M.hexName = hex_array[i][j][0]
          self.market_list.append(M)
          self.market_dict[hex_array[i][j][0]] = M
    #ipdb.set_trace()
    for i in range(0,len(self.market_list)):
      traders = self.market_list[i].traders
      for j in range(0,len(traders)):
        if j < i:
          if self.market_list[j].government != self.market_list[i].government:
            traders[j].type2 = 'ForeignTrader'
            traders[j].currency_index = self.market_list[i].government.currency_index
          traders[j].other_market = self.market_list[j]
          traders[j].other_trader = self.market_list[j].traders[j]
        else:
          if self.market_list[j+1].government != self.market_list[i].government:
            traders[j].type2 = 'ForeignTrader'
            traders[j].currency_index = self.market_list[i].government.currency_index
          traders[j].other_market = self.market_list[j+1]
          traders[j].other_trader = self.market_list[j+1].traders[j]
    self.CountryList = self.reorder_list(self.CountryList, self.CountryNameList)

  def run_turn(self, num_turns):
    for t in range(0, num_turns):
      self.trade_balance = [[0 for i in range(0,len(self.CountryList))] for i in range(0,len(self.CountryList))]
      self.determine_exchange_rates()
      for i in range(0,len(self.CountryList)):
        self.CountryList[i].append_variable_list()
      for i in range(0,len(self.market_list)):
        self.market_list[i].run_market(1)
        for j in self.currency_indexes:
          self.foreign_investment[j - self.currency_indexes[0]][self.market_list[i].government.index] += self.market_list[i].supply_history[j][-1]
      for i in range(0,len(self.CountryList)):
        self.CountryList[i].record_data()
        self.CountryList[i].normalize_variable_list()
      for i in range(0,len(self.balance)):
        self.trade_balance_history[i].append(self.balance[i])

  def display_graphs(self, num_turn):
    for i in range(0,len(self.market_list)):
        print(self.location_names[i])
        self.market_list[i].display_price_history(num_turn)
        self.market_list[i].display_graphs(num_turn)
      
    plt.title('Trade Balances')
    for i in range(0,len(self.trade_balance_history)):
      plt.plot(self.trade_balance_history[i][num_turn:], label=self.CountryNameList[i])
    plt.ylabel('Amount')
    plt.xlabel('Years')
    plt.legend()
    plt.show()
  
  def display_compare_graphs(self, num_turn, top_num):
    plt.title('Trade Balances')
    for i in range(0,len(self.trade_balance_history)):
      plt.plot(self.trade_balance_history[i][num_turn:], label=self.CountryNameList[i])
    plt.ylabel('Amount')
    plt.xlabel('Years')
    plt.legend()
    plt.show()

    self.create_exchange_rate_graph(num_turn)

    for i in range(0, min(top_num, len(self.CountryList[0].var_list))):
      plt.title(self.CountryList[0].var_list[i])
      for j in range(0,len(self.CountryList)):
          plt.plot(getattr(self.CountryList[j], self.CountryList[0].var_list[i])[num_turn:], label=self.CountryList[j].GovName)
      plt.ylabel(self.CountryList[0].var_list[i])
      plt.xlabel('Years')
      plt.legend()
      plt.show()
        
  def display_prices(self):
    for i in range(0,len(self.market_list)):
      print(self.location_names[i])
      self.market_list[i].display_prices()

  def get_prices(self, M_list, good_index, sticky):
    #if good_index == 0 or good_index == 4:
    #ipdb.set_trace()
    top = 0
    for k in range(0,len(M_list)):
      country_index = self.CountryList.index(M_list[k].government)
      if M_list[k].government.currency_index == good_index:
        for j in range(0,len(M_list[k].goods_supply)):
          if j != good_index:
            middle = 0
            for i in range(0,len(M_list[k].households)):
              middle += M_list[k].households[i].goods_pref[-1]*(M_list[k].households[i].endowments[j])
            top += middle*M_list[k].prices[j]*self.exchangeRateArr[country_index][-1]
      else:
        for j in range(0,len(M_list[k].goods_supply)):
          if j != good_index:
            middle = 0
            for i in range(0,len(M_list[k].households)):
              middle += M_list[k].households[i].goods_pref[good_index]*(M_list[k].households[i].endowments[j])
            top += middle*M_list[k].prices[j]*self.exchangeRateArr[country_index][-1]
    bottom = 0
    for k in range(0,len(M_list)):
      if M_list[k].government.currency_index == good_index:
        for i in range(0,len(M_list[k].households)):
          bottom += (1 - M_list[k].households[i].goods_pref[-1])*(M_list[k].households[i].endowments[-1])
      else:
        for i in range(0,len(M_list[k].households)):
            bottom += (1 - M_list[k].households[i].goods_pref[good_index])*(M_list[k].households[i].endowments[good_index])
    if bottom == 0:
      return 1
    elif good_index > 1:
      new_price = top/bottom
      return new_price
      #self.prices[good_index] = self.prices[good_index] + sticky*(new_price - self.prices[good_index])
    else:
      return top/bottom
    if top == 0:
      print("Error with this price: ", good_index)
    #return self.prices[good_index]

  def determine_exchange_rates(self):
    #pdb.set_trace()
    total = 0
    for i in range(0,len(self.currency_indexes)):
      new_rate = self.get_prices(self.market_list, self.currency_indexes[i], 0.3)
      self.exchangeRateArr[i].append(new_rate)
      total += new_rate
    for i in range(0,len(self.currency_indexes)):
      self.exchangeRateArr[i][-1] = (self.exchangeRateArr[i][-1]/total)*10
    #for i in range(0,5):
    #for j in range(0,len(self.currency_indexes)):
    #self.exchangeRateArr[j][-1] = (self.get_prices(self.market_list, self.currency_indexes[j], 0.3))
    for i in range(0, len(self.market_list)):
      for j in range(0, len(self.currency_indexes)):
        if i != j:
          self.market_list[i].prices[self.currency_indexes[j]] = (self.exchangeRateArr[j][-1])*(1/self.exchangeRateArr[self.market_list[i].government.index][-1])

  def get_amounts(self, household_index, good_index):
    #print(good_index)
    self.households[household_index].goods_supply[good_index] = (self.households[household_index].goods_pref[good_index]/self.prices[good_index])*(sum([(self.households[household_index].endowments[i])*self.prices[i] for i in range(0,len(self.goods_supply))]))
    return self.households[household_index].goods_supply[good_index]

  def get_country(self, name):
    return self.CountryList[self.CountryNameList.index(name)]

  def switch_hex(self, hex, to, g=None):
    market = self.market_list[self.location_names.index(hex)]
    prev_gov = market.government
    prev_gov.markets.remove(market)
    country_to = self.get_country(to)
    country_to.markets.append(market)
    for trader in range(0,len(market.traders)):
      if market.traders[trader].other_market.government == country_to:
        market.traders[trader].type2 = "Trader"
      elif market.traders[trader].other_market.government == prev_gov:
        market.traders[trader].type2 = "ForeignTrader"
    market.government = country_to
    market.households[-2] = country_to
    market.households[-1] = country_to.TaxCollector
    if g != None:
      g.save()
  
  def budget_graph(self, country, start, file_path=None):
    def add_trace(fig, y, net, color, title, green_num=0, red_num=0,blue_num=0, negative=1, fill2='tonexty'):
      fig.add_trace(go.Scatter(x=[i for i in range(0,len(net))], y=[negative*y[i] + net[i] for i in range(0,len(net))],
        fill=fill2,
        mode='lines',
        line_color='black',
        fillcolor = 'rgba('+str(red_num)+', '+str(green_num)+', 0, 0.5)',
        name=title
        ))
    #print('rgba('+str(red_num)+', '+str(green_num)+', '+str(blue_num)+', 0.5)')
    def collection2(fig, collection, total, labels, net,color):
      sum = [i for i in total]
      add_trace(fig, total, net,'green', labels[0],155,0,0,1,None)
      for i in range(1,len(collection)):
        sum = [sum[j] - collection[i-1][j] for j in range(0,len(total))]
        add_trace(fig, sum, net,'green',labels[i], (100*i)% 255)

    def collection3(fig, collection, total, labels, net,color):
      sum = [0 for i in total]
      #add_trace(fig, total, net,'green', labels[0],color,0,1,None)
      for i in range(0,len(collection)):
        sum = [sum[j] + collection[i][j] for j in range(0,len(total))]
        add_trace(fig, sum, net,'green',labels[i], (80*(i)) % 255, 255, (80*(i)) % 255,-1)
    country = self.get_country(country)
    Corporate_Tax = country.CorporateTaxArray[start:-1]
    #print(Corporate_Tax)
    Income_Tax = country.IncomeTaxArray[start:-1]
    Tarriffs = country.TarriffCollectionArray[start:-1]
    revenues = [Corporate_Tax[i] + Income_Tax[i] + Tarriffs[i] for i in range(0,len(Corporate_Tax))]
    
    net = [0 for i in range(0,len(country.Government_SavingsArray[start:-1]))]#country.Government_SavingsArray[start:-1] #[1000, 1200, 1100, 800]
    collection = [Corporate_Tax, Income_Tax, Tarriffs]
    expense = [country.GovWelfareArray[start:-1],country.InfrastructureArr[start:-1],country.ScienceBudgetArr[start:-1],country.MilitaryArr[start:-1],country.EducationArray[start:-1], country.SubsidyArr[start:-1]]
    expenses = [sum([expense[j][i] for j in range(0,len(expense))]) for i in range(0,len(expense[0]))]
    #print(expenses)
    #debt = [1000, -800, -900, -1100]
    fig = go.Figure()
    fig.update_layout(title_text='Debt and Budget', title_x=0.5)
    #pdb.set_trace()
    collection2(fig, collection, revenues, ['Corporate Tax', 'Income Tax', 'Tarriffs'], net, 255)
    fig.add_trace(go.Scatter(
        x=[i for i in range(0,len(Corporate_Tax))],
        y=net,
        fill='tonexty', # fill area between trace0 and trace1
        name='Net Savings',
        mode='lines', line_color='black',
        fillcolor = 'green',
        line=dict(width=10)
        ))
    #pdb.set_trace()
    collection3(fig, expense, expenses, ['Welfare', 'Infrastructure', 'Science', 'Military', 'Education','Subsidies'], net, 255)
    if file_path == None:
      fig.show()
    else:
      fig.write_html(file_path)
  ##Transfer money between countries. Transfer array is similar to tariff array, each row represnting the transfer wishes of one country
  def trade_money(self, transfer_array):
  #i is the destination country, j is the source country.
    Countries = self.CountryList
    for i in range(0, len(Countries)):
      for j in range(0, len(Countries)):
        #am = transfer_array[j][i]*(self.exchangeRateArr[j][-1]/self.exchangeRateArr[i][-1])
        am2 = transfer_array[j][i]
        Countries[i].goods_supply[self.currency_indexes[j]] += am2
        Countries[j].Government_Savings -= am2
        Countries[j].deficit -= am2

  #Transfer military goods between countries. Transfer array is similar to tariff array, each row represnting the transfer wishes of one country
  def trade_military_goods(self, transfer_array):
  #i is the destination country, j is the source country.
    Countries = self.CountryList
    for i in range(0, len(Countries)):
      for j in range(0, len(Countries)):
        am = transfer_array[j][i]
        if Countries[j].goods_supply[Countries[j].MilitaryIndex] > am:
          Countries[i].goods_supply[Countries[i].MilitaryIndex] += am
          Countries[j].goods_supply[Countries[j].MilitaryIndex] -= am

  def create_exchange_rate_graph(self, start):
        data = {'Country': [],
        'Exchange Rate': [],
        'Year':[]
        }
        for j in range(0, len(self.exchangeRateArr)):
            data['Exchange Rate'] += self.exchangeRateArr[j][start:]
            data['Year'] += [i for i in range(0,len(self.exchangeRateArr[j][start:]))]
            data['Country'] += [self.CountryNameList[j] for i in range(0,len(self.exchangeRateArr[j][start:]))]
        fig = px.line(data, x='Year', y='Exchange Rate',title="Exchange Rates", color="Country")
        fig.update_xaxes(title="Year")
        fig.update_yaxes(title="Amount")
        fig.show()
        fig.write_html("dist/WOM/templates/App/graphs/exchange.html")

  def reorder_list(self, original_objects, order_list):
    order_dict = {string: index for index, string in enumerate(order_list)}
    
    sorted_objects = sorted(original_objects, key=lambda x: order_dict.get(x.GovName, float('inf')))
    
    return sorted_objects

def create_income_barchart(incomes, num_bins):
    # Create the histogram of income data
    _, bins, _ = plt.hist(incomes, bins=num_bins)
    
    # Set the labels and title
    plt.xlabel('Income')
    plt.ylabel('Count')
    plt.title('Income Distribution')
    
    # Display the bar chart
    plt.show()

# Example usage
#income_list = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
#income_list = [1000, 2000, 2000, 4000, 4000, 6000, 6000, 8000, 9000, 10000]
#num_bins = 5
#create_income_barchart(income_list, num_bins)

def trade_diagram(CountryNames, tradeBalance, name, goodBalance=False, index=0):
  if goodBalance:
    tradeBalance = [tradeBalance[i][index] for i in range(0,len(tradeBalance))]
  new_trade_balance = []
  for i in range(0,len(tradeBalance)):
    for j in range(0,len(tradeBalance[i])):
      if i != j:
        new_trade_balance.append(tradeBalance[i][j]*10)
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
  fig.write_html("dist/WOM/templates/App/graphs/"+name+".html")


def create_color_array(length, opacity, multiplier):
  arr = []
  for j in range(0,multiplier):
    for i in range(0,length):
      arr.append('hsla(' + str(i*25) + ', 100%, 50%, 0.4)')
  return arr
