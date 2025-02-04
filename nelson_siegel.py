import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import minimize


def yearfrac(start_date, end_date):
    '''Calculates the time between dates in years by dividing with average number of days in a year'''
    return (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365.25


def bond_cashflow_setup(bond_data, last_yield):
    '''Sets up the cashflow of a bond given {Payment dates, Cashflows and yield}'''
    for i in range(len(bond_data)):
        bond_data.loc[i, 'Payment Time'] = yearfrac(today, bond_data.loc[i, 'Payment Date'])
 
    bond_data['Discount Factor'] = 1 / (1 + last_yield) ** bond_data['Payment Time']
    bond_data['CF x DF'] = bond_data['Cashflow'] * bond_data['Discount Factor']


def nelson_siegel_rate(maturity, theta0, theta1, theta2, lamda):
    '''Calculates the continously compounded rate in the Nelson Siegel model'''
    tau = maturity
    term1 = theta0
    term2 = theta1 * (1 - np.exp(-tau / lamda)) / (tau / lamda)
    term3 = theta2 * ((1 - np.exp(-tau / lamda)) / (tau / lamda) - np.exp(-tau / lamda))
    return term1 + term2 + term3


def nelson_siegel_df(maturity, theta0, theta1, theta2, lamda):
    '''Calculates discount factor in the NS model at a given maturity'''
    tau = maturity
    term1 = theta0
    term2 = theta1 * (1 - np.exp(-tau / lamda)) / (tau / lamda)
    term3 = theta2 * ((1 - np.exp(-tau / lamda)) / (tau / lamda) - np.exp(-tau / lamda))
    return np.exp(-(term1 + term2 + term3) * tau)


def nelson_siegel_price(cashflows, maturities, theta0, theta1, theta2, lamda):
    '''Prices a coupon bond in the Nelson Siegel Model'''
    price = 0
    for i in range(len(maturities)):
        tau = maturities[i]
        term1 = theta0
        term2 = theta1 * (1 - np.exp(-tau / lamda)) / (tau / lamda)
        term3 = theta2 * ((1 - np.exp(-tau / lamda)) / (tau / lamda) - np.exp(-tau / lamda))
        discount_factor = np.exp(-(term1 + term2 + term3) * tau)
        
        price += cashflows[i] * discount_factor
    return price


def loss_function(params, cashflows_list, maturities_list, observed_prices):
    '''Sets up a least squares problem between Nelson Siegel prices and observed prices'''
    theta0, theta1, theta2, lamda = params
    predicted_prices = []
    
    for i in range(len(cashflows_list)):
        predicted_price = nelson_siegel_price(cashflows_list[i], maturities_list[i], theta0, theta1, theta2, lamda)
        predicted_prices.append(predicted_price)
    
    errors = np.array(predicted_prices) - np.array(observed_prices)
    return np.sum(errors**2)


def rate_convertion(continuous_rate):
    '''Converts Continuously compounded rates to anually compounded rates'''
    return np.exp(continuous_rate) - 1


###### START OF MAIN ######



yield_list = [0.0915, 0.0814, 0.0693, 0.0635] # Last yields

today = '2024-09-12'


# Setup RIKB 25 0612 cashflow
RIKB_25_0612 = pd.DataFrame({'Period': [1],
                             'Payment Date': ['2025-06-12'],
                             'Cashflow': [108]})

bond_cashflow_setup(bond_data=RIKB_25_0612, last_yield=yield_list[0])


# Setup RIKB 27 0415 cashflow
RIKB_27_0415 = pd.DataFrame({'Period': [1, 2, 3],
                             'Payment Date': ['2025-04-15', '2026-04-15', '2027-04-15'],
                             'Cashflow': [8, 8, 108]})

bond_cashflow_setup(bond_data=RIKB_27_0415, last_yield=yield_list[1])


# Setup RIKB 31 0124 cashflow
RIKB_31_0124 = pd.DataFrame({'Period': [1, 2, 3, 4, 5, 6, 7],
                             'Payment Date': ['2025-01-24', '2026-01-24', '2027-01-24', '2028-01-24', '2029-01-24', '2030-01-24', '2031-01-24'],
                             'Cashflow': [6.5, 6.5, 6.5, 6.5, 6.5, 6.5, 106.5]})

bond_cashflow_setup(bond_data=RIKB_31_0124, last_yield=yield_list[2])

# Setup RIKB 42 0217 cashflow
RIKB_42_0217 = pd.DataFrame({'Period': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                             'Payment Date': ['2025-02-17', '2026-02-17', '2027-02-17', '2028-02-17', '2029-02-17', '2030-02-17',
                                              '2031-02-17', '2032-02-17', '2033-02-17', '2034-02-17', '2035-02-17', '2036-02-17',
                                              '2037-02-17', '2038-02-17', '2039-02-17', '2040-02-17', '2041-02-17', '2042-02-17',],
                             'Cashflow': [4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 104.5]})

bond_cashflow_setup(bond_data=RIKB_42_0217, last_yield=yield_list[3])


# Maturities (in years) corresponding to the bonds
maturities_list = [
    RIKB_25_0612['Payment Time'].values, 
    RIKB_27_0415['Payment Time'].values, 
    RIKB_31_0124['Payment Time'].values,  
    RIKB_42_0217['Payment Time'].values   
]

df_list = [
    RIKB_25_0612['Discount Factor'].values,
    RIKB_27_0415['Discount Factor'].values,
    RIKB_31_0124['Discount Factor'].values,
    RIKB_42_0217['Discount Factor'].values
]

# Cashflows corresponding to the bonds
cashflows_list = [
    RIKB_25_0612['Cashflow'].values,  
    RIKB_27_0415['Cashflow'].values, 
    RIKB_31_0124['Cashflow'].values,  
    RIKB_42_0217['Cashflow'].values   
]

# Observed bond prices (dirty prices)
observed_prices = [
    RIKB_25_0612['CF x DF'].sum(),
    RIKB_27_0415['CF x DF'].sum(),
    RIKB_31_0124['CF x DF'].sum(),
    RIKB_42_0217['CF x DF'].sum()
]

initial_params = [0.05, -0.04, 0.03, 0.2]

# Perform the optimization
result = minimize(
    loss_function,
    initial_params,
    args=(cashflows_list, maturities_list, observed_prices),
    method='L-BFGS-B'
)

theta0_opt, theta1_opt, theta2_opt, lamda_opt = result.x

print(f"Optimized Parameters: theta0={theta0_opt}, theta1={theta1_opt}, theta2={theta2_opt}, lamda={lamda_opt}")



# Plot the price fit
nelson_siegel_prices = [nelson_siegel_price(cashflows_list[0], maturities_list[0], theta0_opt, theta1_opt, theta2_opt, lamda_opt), 
                        nelson_siegel_price(cashflows_list[1], maturities_list[1], theta0_opt, theta1_opt, theta2_opt, lamda_opt), 
                        nelson_siegel_price(cashflows_list[2], maturities_list[2], theta0_opt, theta1_opt, theta2_opt, lamda_opt), 
                        nelson_siegel_price(cashflows_list[3], maturities_list[3], theta0_opt, theta1_opt, theta2_opt, lamda_opt)]

plt.scatter([RIKB_25_0612['Payment Time'].iloc[-1], RIKB_27_0415['Payment Time'].iloc[-1], 
             RIKB_31_0124['Payment Time'].iloc[-1], RIKB_42_0217['Payment Time'].iloc[-1]], 
             observed_prices)

plt.scatter([RIKB_25_0612['Payment Time'].iloc[-1], RIKB_27_0415['Payment Time'].iloc[-1], 
             RIKB_31_0124['Payment Time'].iloc[-1], RIKB_42_0217['Payment Time'].iloc[-1]], 
             nelson_siegel_prices, marker='*')
plt.show()


# Plot the discount factor fit
tau_list = np.linspace(0.1, 20, 1000)
nelson_siegel_df_curve = [nelson_siegel_df(tau, theta0_opt, theta1_opt, theta2_opt, lamda_opt) for tau in tau_list]

plt.figure(figsize=(13, 6))
plt.plot(tau_list, nelson_siegel_df_curve, label='Model', color='black', linewidth=1)
plt.scatter(
    [RIKB_25_0612['Payment Time'].iloc[-1], RIKB_27_0415['Payment Time'].iloc[-1], 
     RIKB_31_0124['Payment Time'].iloc[-1], RIKB_42_0217['Payment Time'].iloc[-1]], 
    [df_list[0][-1], df_list[1][-1], df_list[2][-1], df_list[3][-1]],
    color='black', s=35, label='Observed'
)
plt.legend()
plt.xlabel('Time to Maturity')
plt.ylabel('Discount Factor')
plt.grid(True)
plt.show()


# Extract the rates from the discount factors for different maturities
yield_from_discount_factors = [(1 / df) ** (1 / tau) - 1 for df, tau in zip(nelson_siegel_df_curve, tau_list)]

# Plot the derived yields from discount factors
plt.figure(figsize=(13, 6))
plt.plot(tau_list, yield_from_discount_factors, label='Model', color='black', linewidth=1)
plt.scatter(
    [RIKB_25_0612['Payment Time'].iloc[-1], RIKB_27_0415['Payment Time'].iloc[-1], 
     RIKB_31_0124['Payment Time'].iloc[-1], RIKB_42_0217['Payment Time'].iloc[-1]], 
     yield_list, 
     color='black', s=35, label='Observed'
)
plt.legend()
plt.xlabel('Time to Maturity')
plt.ylabel('Yield')
plt.grid(True)
plt.show()


# now plot the yield curve (both continuously compounded rate as provided by nelson sigel then converted to anually compounded)
nelson_siegel_curve = [nelson_siegel_rate(tau, theta0_opt, theta1_opt, theta2_opt, lamda_opt) for tau in tau_list]
nelson_siegel_curve_annual = [rate_convertion(rate) for rate in nelson_siegel_curve]

plt.figure(figsize=(13, 6))
plt.plot(tau_list, nelson_siegel_curve, label='Model Continuous Rate', color='black', linewidth=1, linestyle='--')
plt.plot(tau_list, nelson_siegel_curve_annual, label='Model Annual Rate', color='black', linewidth=1)
plt.scatter([RIKB_25_0612['Payment Time'].iloc[-1], RIKB_27_0415['Payment Time'].iloc[-1], 
             RIKB_31_0124['Payment Time'].iloc[-1], RIKB_42_0217['Payment Time'].iloc[-1]], 
             yield_list,
             color='black', s=35, label='Observed')
plt.legend()
plt.xlabel('Time to Maturity')
plt.ylabel('Discount Factor')
plt.grid(True)
plt.show()