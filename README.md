# Bond-Math

## This repository is aimed at fitting the Icelandic spot rate curves through various techniques. 

### The Nelson Siegel Model

The aim of the first problem is to fit a Nelson-Siegel model to the Icelandic non-indexed government bond market. These particular bonds go by the abbreviation "RIKB" followed by the date of their maturity. The problem prompts us to select four different bonds with varying maturity times over which to fit the model. The following table lists the chosen bonds along with their respective specifications as of the 12th of September 2025. 

| Bond       | Maturity Date | Coupon | Last Yield | Frequency |
|------------|--------------|--------|------------|------------|
| RIKB 25 0612 | 12/6/2025  | 8%  | 0.0915  | Annual |
| RIKB 27 0415 | 15/4/2027  | 8%  | 0.0814  | Annual |
| RIKB 31 0124 | 24/1/2031  | 6.5%  | 0.0693  | Annual |
| RIKB 42 0217 | 17/2/2042  | 4.5%  | 0.0635  | Annual |

Having selected the bonds, we proceed to set up their cash flows assuming a principal of 100 and payment times calculated in yearly terms as the difference in days between now and the next payment divided by 365.25. This facilitates the calculation of each bond's dirty price as the sum of its discounted cash flow according to 

$$
    P_{dirty}(0, T) = c_i \sum_{i=1}^{n} \frac{1}{(1+y)^{T_i}} + \frac{100}{(1+y)^{T_n}}
$$

Where $c_i$ is the cash flow at $T_i$ and $y$ is the observed last yield. The following code snippet demonstrates this logic for one of the bonds

![Price Calculation](./images/price_calc_code.png)


Summing up the discounted cash flows for each bond produces the dirty price vector given by,

$$
\mathbf{P}_{dirty} =
\begin{pmatrix}
    101.1588 \\
    102.9097 \\
    101.9178 \\
    83.3506
\end{pmatrix}
$$

Having calculated the dirty prices of each security we can proceed to fitting the model. The Nelson-Siegel model assumes a parametric functional form for the discount factor $Z(0,T)$ given by

$$
    Z(0, T) = e^{-r(0, T)T} 
$$

Where the continuously compounded yield is given by

$$
r(0, T) = \theta_0 + (\theta_1 + \theta_2)\frac{1-e^{-\frac{T}{\lambda}}}{\frac{T}{\lambda}} - \theta_2 e^{-\frac{T}{\lambda}}
$$

And the terms $\Theta = (\theta_0, \theta_1, \theta_2, \lambda)$ are to be estimated from empirical data. The methodology of estimating the parameters proves to be quite straight-forward; Each bond $i \in \{1,2,3,4\}$ with coupon payment $c_i$ and cash flow payment dates $T_j^i$, for $j = 1,..., n$ can be priced in the Nelson-Siegel model according to 

$$
    P_c^{i, NS} = c_i \sum_{j=1}^{n_i} e^{-(\theta_0 + (\theta_1 + \theta_2)\frac{1-e^{-\frac{T_j}{\lambda}}}{\frac{T_j}{\lambda}} - \theta_2 e^{-\frac{T_j}{\lambda}})T_j} + 100 \cdot e^{-(\theta_0 + (\theta_1 + \theta_2)\frac{1-e^{-\frac{T_{n_i}}{\lambda}}}{\frac{T_{n_i}}{\lambda}} - \theta_2 e^{-\frac{T_{n_i}}{\lambda}})T_{n_i}}
$$

Now for the same bond, we have already calculated the dirty price from empirical data. As such we can compute the square of errors between the model price and empirical price for a given set of elements in $\Theta$, namely

$$
    E(\theta_0, \theta_1, \theta_2, \lambda) = \sum_{i=1}^{4} (P_c^{i, NS} - P_{dirty}^{i})^2
$$

If we optimize the parameters $\theta_0, \theta_1, \theta_2, \lambda$ to minimize $E$, we obtain the set of parameters that best fit the Nelson-Siegel model to the market as seen in the following code snippet

![NS fitting code](./images/NS_fitting_code.png)

Having optimized the parameters to fit the model prices to those empirically observed, we can move forward and pass the parameters through the pricing function given the same cash flows and maturities as the empirical bonds. Plotting the output alongside the observed data gives us a means to assess our fit.

![Model fit](./images/model_fit.png)



We produce a very good fit with minimal error. Moving closer to the heart of the problem, we plot the discount curve produced by the optimized model parameters as a function of $T$ along with those empirically calculated according to the bond yields. 

![DF calc](./images/df_calculation_code.png)


![NS DFs](./images/NS_DFs.png)


At last, we can extract the annually compounded yields from the model discount factors by solving for $y$ in the formula for the discount factor given annual compounding, namely

$$
    Z(0, T) = \frac{1}{(1 + y)^T} \ \Rightarrow \ y = \left( \frac{1}{Z(0, T)}\right)^{\frac{1}{T}} - 1 
$$

Doing this for all modelled discount factors produces the following plot 

![NS Yields Structure](./images/NS_Yields.png)


Alternatively, one can simply pass the optimized parameters through the Nelson-Siegel yield formula given by equation above. However, this would result in the continuously compounded yield curve which would not be directly comparable to the observed yields given in annual compounding. To account for the discrepancy, every yield produced by the model should be converted to an annual basis. The following plot aims to visually represent the difference.

![NS Yields Structure Comparison](./images/NS_Yields_comparison.png)


The Nelson-Siegel model shows promising fitment of the bond prices in our case. However, we do see some breakdown in the fit to the yields themselves. This might be caused by the non-linear relationship of bond prices and yields, as prices are inversely related to yields in a convex manner. As such, small changes in yields can have different effects on prices depending on yield level and maturity times. Our model is specifically designed to minimize residuals in the prices rather than yields and does so well. The convexity in the relationship means that the bonds at farther maturities are much more sensitive to yields and as a result, even though the prices are well fit the corresponding yields are less accurate. 

This can be combated by a possible penalty term that balances the fit between prices and yields by introducing some penalty for mismatched yields at long maturities, or possibly by adding the Svensson extension to the model. 

It is also worth mentioning that bonds at farther maturities are normally less liquid which can result in their prices being more noisy. In that case, our model might be indicating a possible trading opportunity as it predicts a lower yield than that which is observed in the market, implying that the bond is underpriced. According to the model, the market might be overestimating the risk or underpricing these long-term bonds, which could signal a buying opportunity. That is to say, if one has good confidence in the models predictive ability. 
