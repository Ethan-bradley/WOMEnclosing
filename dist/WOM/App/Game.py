from .models import Game, Player, IndTariff, Tariff, Army, Policy, PolicyGroup, Hexes, PlayerProduct, Product, Notification
from .forms import NewGameForm, IndTariffForm, JoinGameForm, AddIndTariffForm, AddTariffForm, NextTurn, ResetTurn
#from .GameEconModel import Country
#from .TradeModel import Trade
from .EconHelper import CreationManager, Manager, trade_diagram
from .EconHelper import Government
from django.core.files import File
from .HexList import HexList
from .HexList2 import HexList2
from .ArmyCombat import ArmyCombat
from django.db.models.fields import *
import os
import matplotlib.pyplot as plt
import matplotlib
import math

class GameEngine():
	def __init__(self, num_players, nameListInput):
		self.nameList = nameListInput
		self.EconEngines = []
		CountryList = nameListInput#['Neutral','Spain','UK','France','Germany','Italy']
		self.CountryNameList = CountryList
		self.nameList = CountryList
		good_names = ['Deposits','Loans','UnskilledLabour','Engineer','Miner','Farmer','Metallurgist','Teacher','Doctor','Physicist','Education','Food','Clothes','Services','Housing','Construction','Healthcare','Military','MedicalEquipment','Steel','Crops','Iron','Coal','Oil','Transport','Machinery']+CountryList+['Money']
		good_types = ['Consumer','Loans','Labour',        'Labour',  'Labour', 'Labour',      'Labour','Labour','Labour','Labour',     'Consumer','Consumer','Consumer','Consumer','Consumer','Capital','Consumer','Other',    'Capital','Capital','Raw','Raw','Raw','Raw',           'Transport','Capital']+['ForeignCurrency' for i in range(len(CountryList))]+['Money']
		industry_types = ['Deposits','Loans','Labour',    'Labour',       'Labour', 'Labour',  'Labour','Labour','Labour','Labour', 'Education','Food',    'Food','Services','Construction','Construction','Health','Military','HealthEquipment','Steel','Agriculture','Iron','Coal','Oil','Transport','Machinery']+['ForeignCurrency' for i in range(len(CountryList))]+['Money']
		transportable_indexes = [11,12,17,18,19,20,21,22,23,25,len(good_names)-1]
		num_households = 30 #30
		num_corp_per_industry = [2 for i in range(len(good_names))] #10

		industry_types2 = ['Deposits','Loans','Labour',    'Labour',       'Labour', 'Labour',  'Labour','Labour','Labour','Labour', 'Education','Food',    'Food','Services','Construction','Construction','Health','Military','HealthEquipment','Steel','Agriculture','Iron','Coal','Oil','Transport','Machinery']+['ForeignCurrency' for i in range(len(CountryList))]+['Chemistry','Physics','Biology','Money']
		industry_value_dict = {
		    'Agriculture':[['Machinery',0.4], ['Farmer',0.2], ['Oil', 0.2], ['Doctor', 0.0]],
		    'Food':[['Construction', 0.2],['Machinery',0.3], ['Crops',0.3], ['UnskilledLabour',0.2], ['Engineer', 0.0]],
		    'Manufacturing':[['Machinery',0.35], ['Construction',0.1], ['Steel',0.15],['UnskilledLabour',0.45], ['Engineer', 0.0]],
		    'Military':[['Machinery',0.15], ['Construction',0.1], ['Steel',0.1], ['Oil',0.1], ['Metallurgist',0.2], ['Engineer',0.35]],
		    'Steel':[['Machinery',0.4], ['Iron',0.1],['Coal',0.1],['Metallurgist',0.45]],
		    'Services': [['Machinery',0.5], ['Oil',0.1], ['UnskilledLabour',0.4]],
		    'Health':[['MedicalEquipment',0.3], ['Construction',0.1], ['UnskilledLabour',0.1], ['Doctor',0.5]],
		    'HealthEquipment':[['Machinery',0.3],['Engineer',0.6]],
		    'Mining':[['Machinery',0.6], ['Miner',0.2],['Engineer',0.0]],
		    'Oil':[['Machinery',0.6], ['Miner',0.2],['Engineer',0.0]],
		    'Iron':[['Machinery',0.4], ['Oil', 0.2], ['Miner',0.2],['Engineer',0.0]],
		    'Coal':[['Machinery',0.4], ['Oil', 0.2], ['Miner',0.2],['Engineer',0.0]],
		    'Transport':[['Construction',0.33],['Oil',0.3], ['UnskilledLabour',0.37],['Engineer',0.0]],
		    'Construction':[['Machinery',0.3], ['Oil', 0.1], ['UnskilledLabour',0.2], ['Engineer',0.4]],
		    'Machinery':[['Machinery',0.4], ['Steel',0.1], ['Metallurgist',0.2], ['Engineer',0.3]],
		    'Deposits':[['Loans',0.4],['Construction',0.2]] + [[i,(1/len(CountryList))*0.2] for i in CountryList] + [['Engineer',0.2]],
		    'Loans':[['Loans',0.5], ['Deposits',0.5]],
		    'Education':[['Construction',0.3], ['Teacher',0.7]],
		    'Chemistry':[['Machinery',0.3], ['Engineer',0.7]],
		    'Biology':[['Machinery',0.3], ['Doctor',0.7]],
		    'Physics':[['Machinery',0.3], ['Physicist',0.7]],
		}
		researcher_indexes, industry_dict = self.create_industry_dict(good_names, good_types, industry_types2,industry_value_dict)
		education_array = [[2,0],[3,7],[4,2],[5,2],[6,4],[7,7],[8,10],[8,10]]
		final_goods = ['Education','Food','Clothes','Services','Housing','Construction','Healthcare','Military','Transport','Capital']
		temp = 0
		if num_players > 7:
			#for i in range(0,num_players):
			#self.EconEngines.append(Country())
			#temp = num_players - 7
			#num_players2 = 7
			hex_list = HexList2().hexList
			#hex_list = HexList().hexList2
			#for i in range(0,num_players2):
			#self.EconEngines[i].run_turn(13)
		else:
			hex_list = HexList().hexList
		M = Manager(hex_list, good_names, good_types, industry_types, num_households, num_corp_per_industry, industry_dict, CountryList, transportable_indexes, education_array, final_goods, researcher_indexes)
		self.EconEngines = M.CountryList
		self.TradeEngine = M
		self.ArmyCombat = ArmyCombat()
		self.var_list = ['Welfare','Education','Military','Infrastructure','Science']
		self.variable_list = ['Welfare','Education','Military','InfrastructureInvest','ScienceInvest']
		self.save_variable_list(self.var_list, num_players)
		#all_players = Player.objects.filter(game=g)
		countries = self.nameList
		self.TarriffsArr = {i:{k:[0.1 for i in range(0,8)] for k in countries} for i in countries}
		#import pdb; pdb.set_trace()
		self.SanctionsArr = {i:{k:[0 for i in range(0,8)] for k in countries} for i in countries}
		self.ForeignAid = {i:{k:[0 for i in range(0,8)] for k in countries} for i in countries}
		self.MilitaryAid = {i:{k:[0 for i in range(0,8)] for k in countries} for i in countries}
		M.run_turn(8) #3 #8 #1
		#trade_diagram(CountryList, self.TradeEngine.trade_balance, "trade")
	def run_more_countries(self, num_players):
		if num_players > 5:
			for i in range(7,num_players):
				self.EconEngines[i].run_turn(13)
	def run_more(self):
		print("Running more")
		self.TradeEngine.run_turn(2) #3
		trade_diagram(self.CountryNameList, self.TradeEngine.trade_balance, "trade")
		self.TradeEngine.create_exchange_rate_graph(8)
	def run_start_trade(self, g, turn_num=7):
		self.run_engine(g)
		for i in range(0,turn_num-2):
			self.run_engine(g, False)
		self.run_engine(g)
	def start_capital(self, g):
		all_players = Player.objects.filter(game=g)
		for p in all_players:
			index = self.nameList.index(p.country.name)
			country = self.get_country(index)
			#self.apply_hex_number(g, p, country)
			self.start_hex_number(g, p, country)

	def run_engine(self, g, graphs=True, years_run=1, projection=False):
		#Resetting model variables
		all_players = Player.objects.filter(game=g)
		if graphs and self.EconEngines[0].time > 5:
			self.set_vars(g, all_players, projection)
		if not projection:
			if g.num_players > 1:
				for p in all_players:
					f = ResetTurn(instance=p)
					pla = f.save(commit=False)
					pla.ready = False
					pla.projection_unloaded = True
					pla.save()
				neutral_player2 = Player.objects.filter(name="Neutral")[0]
				neutral_player2.ready = True
				neutral_player2.save()
			else:
				p = Player.objects.filter(user=g.host)[0]
				print(p.name)
				f = ResetTurn(instance=p)
				pla = f.save(commit=False)
				pla.ready = False
				pla.save()
			all_armies = Army.objects.filter(game=g)
			for a in all_armies:
				a.moved = False
			self.ArmyCombat.doCombat(g)
		#Running engine
		#self.fix_variables()
		self.TradeEngine.run_turn(years_run)
		
			#e.save_GoodsPerCapita('default_graph.png')
		#self.fix_variables()
		#self.TradeEngine.trade(self.EconEngines, [[0.0 for i in range(0,len(self.EconEngines))] for i in range(0,len(self.EconEngines))], [[0.0 for i in range(0,len(self.EconEngines))] for i in range(0,len(self.EconEngines))])
		print('running engine')
		#for p in all_players:
		#index = self.nameList.index(p.country.name)
		#country = self.get_country(index)
		#self.apply_hex_number(g, p, country)
		if graphs:
			trade_diagram(self.CountryNameList, self.TradeEngine.trade_balance, "trade")
			self.TradeEngine.create_exchange_rate_graph(8)
			#self.create_graphs(g, all_players)
			#self.create_compare_graph(self.EconEngines, self.nameList, 17, ['GoodsPerCapita','InflationTracker','ResentmentArr','EmploymentRate','ConsumptionArr','InterestRate','GoodsBalance','ScienceArr'],'',g.name, g)
		return [self.EconEngines, self.TradeEngine]


	def game_combat(self, g):
		self.ArmyCombat.doCombat(g)

	def run_graphs(self, g):
		all_players = Player.objects.filter(game=g)
		#self.create_graphs(g, all_players)
		self.create_compare_graph(self.EconEngines, self.nameList, 17, ['GoodsPerCapita','InflationTracker','ResentmentArr','EmploymentRate','ConsumptionArr','InterestRate','GoodsBalance','ScienceArr'],'',g.name, g)
	def get_country(self, index):
		return self.EconEngines[index]

	def get_country_by_name(self, name):
		index = self.nameList.index(name)
		country = self.get_country(index)
		return country

	def get_country_index(self, name):
		index = self.nameList.index(name)
		return index

	def modify_country_by_name(self, name, attr, set_am):
		index = self.nameList.index(name)
		country = self.get_country(index)
		setattr(country, attr, set_am)
		if getattr(country, attr) < 1:
			setattr(country, attr, set_am)

	def get_trade(self, index, var):
		if var == 0:
			return self.TradeEngine
		elif var == 1:
			return self.TradeEngine.currencyReserves[index]
		elif var == 2:
			return self.TradeEngine.exchangeRates[index]
		elif var == 3:
			return self.TradeEngine.Tariffs[index]

	def create_compare_graph(self, CountryList, CountryName, start, attribute_list, file_path, game_name, g):
		if (os.path.exists('.'+g.GoodsPerCapita.url) and g.GoodsPerCapita.name != 'default_graph.png'):
			os.remove('.'+g.GoodsPerCapita.url)
			os.remove('.'+g.Inflation.url)
			os.remove('.'+g.Resentment.url)
			os.remove('.'+g.Employment.url)
			os.remove('.'+g.Consumption.url)
			os.remove('.'+g.InterestRate.url)
			os.remove('.'+g.GoodsBalance.url)
			os.remove('.'+g.ScienceArr.url)
		a = []
		matplotlib.use('Agg')
		for j in range(0, len(attribute_list)):
			plt.clf()
			plt.title(attribute_list[j])
			for i in range(0,len(CountryList)):
				plt.plot(getattr(CountryList[i],attribute_list[j])[start:],label=CountryName[i])
				plt.ylabel(attribute_list[j])
				plt.xlabel('Years')
				plt.legend()
			plt.savefig(file_path+game_name+attribute_list[j])
			a.append(file_path+game_name+attribute_list[j])
			plt.clf()
		plt.close()

		with open(a[0] +'.png', 'rb') as f:
			g.GoodsPerCapita = File(f)
			g.save()
		os.remove(a[0] +'.png')

		with open(a[1] +'.png', 'rb') as f:
			g.Inflation = File(f)
			g.save()
		os.remove(a[1] +'.png')
		
		with open(a[2] +'.png', 'rb') as f:
			g.Resentment = File(f)
			g.save()
		os.remove(a[2] +'.png')

		with open(a[3] +'.png', 'rb') as f:
			g.Employment = File(f)
			g.save()
		os.remove(a[3] +'.png')

		with open(a[4] +'.png', 'rb') as f:
			g.Consumption = File(f)
			g.save()
		os.remove(a[4] +'.png')

		with open(a[5] +'.png', 'rb') as f:
			g.InterestRate = File(f)
			g.save()
		os.remove(a[5] +'.png')

		with open(a[6] +'.png', 'rb') as f:
			g.GoodsBalance = File(f)
			g.save()
		os.remove(a[6] +'.png')

		with open(a[7] +'.png', 'rb') as f:
			g.ScienceArr = File(f)
			g.save()
		os.remove(a[7] +'.png')

	def set_vars(self, g, all_players, projection=False):
		transfer_array = [[0 for j in range(0,len(self.EconEngines))] for i in range(0,len(self.EconEngines))]
		military_transfer = [[0 for j in range(0,len(self.EconEngines))] for i in range(0,len(self.EconEngines))]
		for p in all_players:
			index = self.nameList.index(p.country.name)
			country = self.get_country(index)

			#self.calculate_differences(g, p, country)
			#self.get_hex_numbers(g, p, country)

			country.IncomeTax = p.IncomeTax
			country.CorporateTax = p.CorporateTax
			#country.GovGoods = p.Education + p.Military
			#revenue = p.IncomeTax*country.money[0] + p.CorporateTax*country.money[4]
			
			country.interest_rate = p.Interest_Rate
			country.deposit_rate = p.Interest_Rate - 0.03
			
			#import pdb; pdb.set_trace();
			welfare = p.Welfare + p.AdditionalWelfare
			country.spending[country.EducationIndex] = p.Education
			country.spending[country.MilitaryIndex] = p.Military
			#country.GovWelfare = p.Welfare + p.AdditionalWelfare
			country.GovWelfare = welfare
			#Investment
			#total_gov_money = revenue + country.BondWithdrawl
			#total_investor_money = country.money[4]*country.InvestmentRate

			#country.GovernmentInvest = gov_invest #p.InfrastructureInvest + p.ScienceInvest
			#total_money = revenue*country.GovernmentInvest + total_investor_money
			country.InfrastructureInvest = p.InfrastructureInvest
			country.ResearchSpend = p.ScienceInvest
			#country.QuickInvestment = p.CapitalInvestment
			#import pdb; pdb.set_trace();

			self.TradeEngine.investment_restrictions[index] = p.investment_restriction

			#Rebellions!!!! EDIT THIS
			#if country.Resentment > 0.06:
			#self.rebel(g, p, country.Resentment)
			#Tarriffs
			#import pdb; pdb.set_trace()
			#try:
			tar = Tariff.objects.filter(game=g, curr_player=p)
			if len(tar) != 0:
				tar = tar[0]
				k = IndTariff.objects.filter(controller=tar)

				count = 0
				for t in k:
					count = self.TradeEngine.CountryNameList.index(t.key.country.name)
					#Save data to array
					self.TarriffsArr[t.key.country.name][p.country.name].append(t.tariffAm)
					self.SanctionsArr[t.key.country.name][p.country.name].append(t.sanctionAm)
					self.ForeignAid[t.key.country.name][p.country.name].append(t.moneySend)
					self.MilitaryAid[t.key.country.name][p.country.name].append(t.militarySend)
					#save data to engines.
					self.TradeEngine.Tariffs[index][count] = t.tariffAm
					self.TradeEngine.Sanctions[index][count] = t.sanctionAm
					transfer_array[index][count] = t.moneySend
					military_transfer[index][count] = t.militarySend
					#import pdb; pdb.set_trace()
					#ADD IN NATIONALIZATION
					#self.TradeEngine.foreign_investment[index][count] = self.TradeEngine.foreign_investment[count][index]*t.nationalization
					count += 1
			#Append variables
			#import pdb; pdb.set_trace()
			self.append_variable_list(self.var_list, self.variable_list, index, p)
			#Product subsidies/restrictions FIX THIS
			productP = PlayerProduct.objects.filter(game=g, curr_player=all_players[index])
			if len(productP) != 0:
				productP = productP[0]
				products = Product.objects.filter(controller=productP)
				country_index = self.nameList.index(p.country.name)
				for product in products:
					index = self.TradeEngine.good_names.index(product.name)
					self.TradeEngine.restrictions[country_index][index] = product.exportRestriction
					country.subsidies[index] = product.subsidy
			#except:
			#	print("Index out of range error!")
			
		#ADD these functions:
		self.TradeEngine.trade_money(transfer_array)
		self.TradeEngine.trade_military_goods(military_transfer)
		if projection:
			return
		hex_list = Hexes.objects.filter(game=g, water=False)
		for h in range(0, len(hex_list)):
			market = self.TradeEngine.market_list[self.TradeEngine.location_names.index(hex_list[h].name)]
			hex_list[h].capital = int(market.output[-1])
			hex_list[h].population = int(market.population[-1])
			resentment = round(market.Resentment[-1],3)
			hex_list[h].resentment = resentment
			if resentment > 0.2:
				self.rebel(g, hex_list[h], resentment)
			hex_list[h].save()

	def save_variable_list(self, var_list, player_num):
		for i in var_list:
			#change to 17
			if i == "Education" or i == "Military":
				setattr(self,i,[[0.01 for i in range(0,8)] for i in range(player_num)])
			else:
				setattr(self,i,[[0.0 for i in range(0,8)] for i in range(player_num)])
	def append_variable_list(self, var_list, variable_list, index, player):
		for i in range(0,len(var_list)):
			getattr(self,var_list[i])[index].append(getattr(player, variable_list[i]))

	def create_graphs(self, g, all_players):
		for p in all_players:
			index = self.nameList.index(p.country.name)
			country = self.get_country(index)
			if not p.robot:
				if (os.path.exists('.'+p.GoodsPerCapita.url) and p.GoodsPerCapita.name != 'default_graph.png'):
					os.remove('.'+p.GoodsPerCapita.url)
					os.remove('.'+p.Inflation.url)
					os.remove('.'+p.RealGDP.url)
					os.remove('.'+p.Employment.url)
					os.remove('.'+p.GovBudget.url)
					os.remove('.'+p.tradeBalance.url)
					os.remove('.'+p.GDPPerCapita.url)
					os.remove('.'+p.InterestRate.url)
					os.remove('.'+p.Capital.url)
					os.remove('.'+p.GoodsProduction.url)
					os.remove('.'+p.GDP.url)
					os.remove('.'+p.GDPGrowth.url)
				#Graphs:
				#country.save_GoodsPerCapita('.'+p.GoodsPerCapita.url)
				a = country.save_graphs('',p.name)
				#print(a[1])
				
				with open(a[0]+'.png', 'rb') as f:
					p.GoodsPerCapita = File(f)
					p.save()
				os.remove(a[0]+'.png')

				
				with open(a[1]+'.png', 'rb') as f:
					p.Inflation = File(f)
					p.save()
				os.remove(a[1]+'.png')
				
				with open(a[2]+'.png', 'rb') as f:
					p.RealGDP = File(f)
					p.save()
				os.remove(a[2]+'.png')
				
				with open(a[3]+'.png', 'rb') as f:
					p.Employment = File(f)
					p.save()
				os.remove(a[3]+'.png')

				with open(a[4]+'.png', 'rb') as f:
					p.GovBudget = File(f)
					p.save()
				os.remove(a[4]+'.png')

				with open(a[5]+'.png', 'rb') as f:
					p.tradeBalance = File(f)
					p.save()
				os.remove(a[5]+'.png')

				with open(a[6]+'.png', 'rb') as f:
					p.GDPPerCapita = File(f)
					p.save()
				os.remove(a[6]+'.png')

				with open(a[7]+'.png', 'rb') as f:
					p.InterestRate = File(f)
					p.save()
				os.remove(a[7]+'.png')

				with open(a[8]+'.png', 'rb') as f:
					p.Capital = File(f)
					p.save()
				os.remove(a[8]+'.png')

				with open(a[9]+'.png', 'rb') as f:
					p.GoodsProduction = File(f)
					p.save()
				os.remove(a[9]+'.png')

				with open(a[10]+'.png', 'rb') as f:
					p.GDP = File(f)
					p.save()
				os.remove(a[10]+'.png')

				with open(a[11]+'.png', 'rb') as f:
					p.GDPGrowth = File(f)
					p.save()
				os.remove(a[11]+'.png')
		
			
	def calculate_differences(self, g, p, e):
	    #g = Game.objects.filter(name=g)[0]
	    #p = Player.objects.filter(name=p)[0]
		policy_list = PolicyGroup.objects.filter(game=g, player=p)
		BalanceList = [0.0 for i in range(11)]
		for pg in policy_list:
			p2 = Policy.objects.filter(policy_group=pg, applied=True)
			if len(p2) <= 0:
				continue
			p2 = p2[0]
			all_fields = p2._meta.get_fields() #_meta.fields
			count = 0
			for a in all_fields:
				if isinstance(a, FloatField):
					n = a.name
					BalanceList[count] += getattr(p2, n)
					count += 1
		#print(BalanceList[0])
		e.SavingsRate = 0.3 + BalanceList[0]
		#print(BalanceList[1])
		e.ConsumptionRate = 0.5 + BalanceList[1]
		#print(BalanceList[2])
		#p.Welfare = BalanceList[2]
		e.Wages = 0.4 + BalanceList[9]
		e.population_growth = 0.02 + BalanceList[10]
		p.save()

	def get_hex_numbers(self, g, p, e):
		hex_list = Hexes.objects.filter(game=g, controller=p, water=False)
		total_population = 0
		total_capital = 0
		total_iron = 0.01
		total_wheat = 0.01
		total_coal = 0.01
		total_oil = 0.01
		for h in hex_list:
			total_population += h.population
			total_capital += h.capital
			total_iron += h.iron
			total_wheat += h.wheat
			total_coal += h.coal
			total_oil += h.oil
		#e.Population = total_population
		#e.capital = total_capital
		e.RawResources[0] = total_iron
		e.RawResources[1] = total_wheat
		e.RawResources[2] = total_coal
		e.RawResources[3] = total_oil
		p.save()


	def apply_hex_number(self, g, p, e):
		hex_list = Hexes.objects.filter(game=g, controller=p, water=False)
		centers = []
		for h in range(0, len(hex_list)):
			if hex_list[h].center:
				centers.append(h)
		#print(centers)
		capital_list = e.create_distribution([0 for j in range(0, len(centers))], centers, e.capital - e.lastcapital, len(hex_list))
		population_list = e.create_distribution([0 for j in range(0, len(centers))], centers, e.Population - e.lastPopulation, len(hex_list))

		#e.lastPopulation = e.Population
		for h in range(0, len(hex_list)):
			print(capital_list[h])
			if not math.isnan(capital_list[h]):
				hex_list[h].capital += int(capital_list[h])
			if not math.isnan(population_list[h]):
				hex_list[h].population += int(population_list[h])
			hex_list[h].save()
			print(hex_list[h].capital)

	def start_hex_number(self, g, p, e):
		hex_list = Hexes.objects.filter(game=g, controller=p, water=False)
		centers = []
		for h in range(0, len(hex_list)):
			if hex_list[h].center:
				centers.append(h)
		#print(centers)
		capital_list = e.create_distribution([0 for j in range(0, len(centers))], centers, e.capital, len(hex_list))
		population_list = e.create_distribution([0 for j in range(0, len(centers))], centers, e.Population, len(hex_list))

		#e.lastPopulation = e.Population
		for h in range(0, len(hex_list)):
			print(capital_list[h])
			hex_list[h].capital += int(capital_list[h])
			hex_list[h].population += int(population_list[h])
			hex_list[h].save()
			print(hex_list[h].capital)

	def printTradeAms(self):
		countryNames = self.nameList
		currencyChangeReserves = self.TradeEngine.currencyChangeReserves 
		string = ""
		for i in range(0,len(currencyChangeReserves)):
			string += "Trade Portfolio of "+countryNames[i]+"\n"
		for j in range(0,len(currencyChangeReserves[0])):
			if i == j:
				continue
		string += "Exports to "+countryNames[j]+": "+str(currencyChangeReserves[i][j])+"\n"
		return string

	def printCurrencyReserves(self):
		countryNames = self.nameList
		currencyReserves = self.TradeEngine.currencyReserves 
		string = ""
		for i in range(0,len(currencyReserves)):
			string += "Currency Reserves of "+countryNames[i]+"\n"
		for j in range(0,len(currencyReserves[0])):
			if i == j:
				continue
		string += "Exports to "+countryNames[j]+": "+str(currencyReserves[i][j])+"\n"
		return string

	def printCurrencyExchange(self):
		countryNames = self.nameList
		currencyRates = self.TradeEngine.exchangeRates 
		string = ""
		for i in range(0,len(currencyRates)):
			string += " "+countryNames[i]
			string += ": "+str(currencyRates[i])+"\n"
		return string
	#Causes a province to rebel.
	def rebel(self, g, hex2, res):
		p = hex2.controller
		if p.name != "Neutral":
			neutral_player = Player.objects.filter(game=g,name="Neutral")[0]
			self.switch_hex(hex2, neutral_player, g)
			Army.objects.create(game=g, size=int(hex2.population*res),controller=neutral_player, naval=False, location=hex2, name=hex2.name+" Rebel Army")
			message2 = "In "+p.name+"'s territory a rebel army of size "+str(round(hex2.population*res*100,0))+" rose up in "+hex2.name
			turn = g.GameEngine.get_country_by_name("UK").time - 6
			Notification.objects.create(game=g, message=message2,year=turn)

	#Switches control of a hex between two players (doesn't work yet)
	def switch_hex(self, h, player_to, g):
		loser = h.controller
		#import pdb; pdb.set_trace()
		to_country = player_to.country.name
		self.TradeEngine.switch_hex(h.name, to_country)
		
		g.save()
		h.controller = player_to
		h.color = player_to.country.color

		h.save()
		player_to.save()
		loser.save()

	def create_industry_dict(self, good_names, goods_type, industry_types, industry_value_dict):
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
