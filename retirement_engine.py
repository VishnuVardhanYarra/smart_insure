"""
Retirement Readiness & Actuarial Financial Gap Engine
Calculates projected retirement living expenses, required corpus, available funds,
financial shortfall/surplus, and dynamic What-If scenario simulations.
"""

import math
import logging

logger = logging.getLogger(__name__)

def format_inr(amount):
    """Formats numeric values into Indian Rupee notation (Cr, L, or comma separated)."""
    if amount is None:
        return "₹0"
    abs_amt = abs(amount)
    sign = "-" if amount < 0 else ""
    if abs_amt >= 10000000:
        return f"{sign}₹{abs_amt / 10000000:.2f} Cr"
    elif abs_amt >= 100000:
        return f"{sign}₹{abs_amt / 100000:.2f} L"
    else:
        return f"{sign}₹{abs_amt:,.0f}"

def calculate_retirement_gap(params):
    """
    Computes comprehensive retirement readiness and financial gap analysis.
    
    Expected params:
        - current_age (int)
        - retirement_age (int)
        - life_expectancy (int, default 85)
        - current_savings (float, e.g. 1000000)
        - monthly_expenses (float, e.g. 50000)
        - monthly_savings (float, regular ongoing SIP/investment, e.g. 20000)
        - expected_retirement_income (float, monthly pension/annuity, default 0)
        - annual_insurance_budget (float, medical & term insurance budget, default 0)
        - inflation_rate (float, annual inflation % e.g. 6.0)
        - pre_retire_roi (float, expected investment return % e.g. 10.0)
        - post_retire_roi (float, conservative retirement return % e.g. 7.0)
    """
    try:
        current_age = max(18, int(params.get('current_age', 30)))
        retirement_age = max(current_age + 1, int(params.get('retirement_age', 60)))
        life_expectancy = max(retirement_age + 1, int(params.get('life_expectancy', 85)))
        
        current_savings = max(0.0, float(params.get('current_savings', 0.0)))
        monthly_expenses = max(0.0, float(params.get('monthly_expenses', 50000.0)))
        monthly_savings = max(0.0, float(params.get('monthly_savings', 15000.0)))
        expected_retirement_income = max(0.0, float(params.get('expected_retirement_income', 0.0)))
        annual_insurance_budget = max(0.0, float(params.get('annual_insurance_budget', 25000.0)))
        
        inflation_rate = float(params.get('inflation_rate', 6.0)) / 100.0
        pre_retire_roi = float(params.get('pre_retire_roi', 10.0)) / 100.0
        post_retire_roi = float(params.get('post_retire_roi', 7.0)) / 100.0
        
        years_to_retire = max(1, retirement_age - current_age)
        years_in_retire = max(1, life_expectancy - retirement_age)
        
        # 1. Projected Living Expenses at Retirement
        # Future value of monthly expenses inflated to retirement age
        inflation_multiplier = math.pow(1.0 + inflation_rate, years_to_retire)
        projected_monthly_expense = monthly_expenses * inflation_multiplier
        projected_annual_expense = projected_monthly_expense * 12.0
        
        # Healthcare buffer inflation (healthcare inflation is historically higher, approx +2%)
        health_inflation_rate = inflation_rate + 0.02
        projected_annual_insurance = annual_insurance_budget * math.pow(1.0 + health_inflation_rate, years_to_retire)
        
        # Total annual requirement minus expected post-retirement income (pension/annuity)
        expected_annual_retire_income = expected_retirement_income * 12.0
        net_annual_expense_needed = max(0.0, (projected_annual_expense + projected_annual_insurance) - expected_annual_retire_income)
        
        # 2. Required Corpus Calculation using Real Rate Annuity
        # Real rate of return during post-retirement phase
        real_rate = (1.0 + post_retire_roi) / (1.0 + inflation_rate) - 1.0
        
        if abs(real_rate) < 0.0001:
            required_corpus = net_annual_expense_needed * years_in_retire
        else:
            # PV of inflation-adjusted growing annuity in retirement
            # PV = E * [1 - (1 + real_rate)^(-N)] / real_rate
            required_corpus = net_annual_expense_needed * (1.0 - math.pow(1.0 + real_rate, -years_in_retire)) / real_rate
        
        # Add 10% emergency healthcare contingency buffer
        healthcare_contingency = required_corpus * 0.08
        required_corpus += healthcare_contingency
        
        # 3. Estimated Available Funds at Retirement
        # Compound growth of current accumulated savings
        fv_current_savings = current_savings * math.pow(1.0 + pre_retire_roi, years_to_retire)
        
        # Future value of ongoing monthly savings (SIP)
        monthly_pre_rate = pre_retire_roi / 12.0
        total_months = years_to_retire * 12
        if monthly_pre_rate > 0:
            fv_monthly_savings = monthly_savings * ((math.pow(1.0 + monthly_pre_rate, total_months) - 1.0) / monthly_pre_rate) * (1.0 + monthly_pre_rate)
        else:
            fv_monthly_savings = monthly_savings * total_months
            
        total_available_corpus = fv_current_savings + fv_monthly_savings
        
        # 4. Financial Gap Analysis (Shortfall or Surplus)
        financial_gap = required_corpus - total_available_corpus
        readiness_percentage = round((total_available_corpus / required_corpus) * 100.0, 1) if required_corpus > 0 else 100.0
        
        # Additional monthly savings required if there is a shortfall
        additional_monthly_savings = 0.0
        if financial_gap > 0 and total_months > 0 and monthly_pre_rate > 0:
            additional_monthly_savings = (financial_gap * monthly_pre_rate) / (((math.pow(1.0 + monthly_pre_rate, total_months) - 1.0) * (1.0 + monthly_pre_rate)))
        
        # Alternative strategy: Years needed to delay retirement to close gap with existing savings rate
        alternative_delay_years = 0
        if financial_gap > 0:
            # Approximate years to close gap: each extra year adds 1 yr compounding + 1 yr less retirement
            annual_compounding_delta = (total_available_corpus * pre_retire_roi) + (monthly_savings * 12.0)
            if annual_compounding_delta > 0:
                alternative_delay_years = max(1, min(10, math.ceil(financial_gap / (annual_compounding_delta * 1.5))))
        
        # Readiness Category Status
        if readiness_percentage >= 100.0:
            status = "surplus"
            status_label = "Fully Funded (Surplus)"
            badge_color = "success"
        elif readiness_percentage >= 75.0:
            status = "moderate_gap"
            status_label = "Moderate Gap (On Track with Minor Adjustment)"
            badge_color = "warning"
        elif readiness_percentage >= 50.0:
            status = "significant_gap"
            status_label = "Significant Shortfall"
            badge_color = "orange"
        else:
            status = "critical_gap"
            status_label = "Critical Shortfall"
            badge_color = "danger"
            
        # Actionable recommendations
        recommendations = []
        if financial_gap > 0:
            recommendations.append(f"Increase your regular monthly SIP by {format_inr(additional_monthly_savings)} to achieve 100% retirement readiness by age {retirement_age}.")
            if alternative_delay_years > 0:
                recommendations.append(f"Alternatively, extending your working career by {alternative_delay_years} year(s) to age {retirement_age + alternative_delay_years} would naturally bridge your retirement corpus gap.")
            recommendations.append(f"Protect against medical inflation with comprehensive Super Top-up Health Insurance to avoid depleting your ₹{format_inr(total_available_corpus)} corpus on late-life treatments.")
        else:
            surplus_amt = abs(financial_gap)
            recommendations.append(f"You have an estimated retirement surplus of {format_inr(surplus_amt)}! You have full financial freedom and could even choose to retire earlier.")
            recommendations.append("Consider setting aside excess surplus into tax-efficient legacy trusts or high-yield dividend funds for generational wealth.")

        return {
            'success': True,
            'current_age': current_age,
            'retirement_age': retirement_age,
            'life_expectancy': life_expectancy,
            'years_to_retire': years_to_retire,
            'years_in_retire': years_in_retire,
            'current_savings': current_savings,
            'monthly_expenses': monthly_expenses,
            'monthly_savings': monthly_savings,
            'expected_retirement_income': expected_retirement_income,
            'annual_insurance_budget': annual_insurance_budget,
            'projected_monthly_expense': projected_monthly_expense,
            'projected_annual_expense': projected_annual_expense,
            'projected_annual_insurance': projected_annual_insurance,
            'net_annual_expense_needed': net_annual_expense_needed,
            'required_corpus': required_corpus,
            'fv_current_savings': fv_current_savings,
            'fv_monthly_savings': fv_monthly_savings,
            'total_available_corpus': total_available_corpus,
            'financial_gap': financial_gap,
            'status': status,
            'status_label': status_label,
            'badge_color': badge_color,
            'readiness_percentage': min(200.0, readiness_percentage),
            'additional_monthly_savings': additional_monthly_savings,
            'alternative_delay_years': alternative_delay_years,
            'assumptions': {
                'inflation_rate': round(inflation_rate * 100.0, 1),
                'pre_retire_roi': round(pre_retire_roi * 100.0, 1),
                'post_retire_roi': round(post_retire_roi * 100.0, 1),
                'real_rate': round(real_rate * 100.0, 2),
                'life_expectancy': life_expectancy,
                'health_inflation_rate': round(health_inflation_rate * 100.0, 1)
            },
            'recommendations': recommendations,
            'formatted': {
                'current_savings': format_inr(current_savings),
                'monthly_expenses': format_inr(monthly_expenses),
                'monthly_savings': format_inr(monthly_savings),
                'expected_retirement_income': format_inr(expected_retirement_income),
                'projected_monthly_expense': format_inr(projected_monthly_expense),
                'projected_annual_expense': format_inr(projected_annual_expense),
                'required_corpus': format_inr(required_corpus),
                'fv_current_savings': format_inr(fv_current_savings),
                'fv_monthly_savings': format_inr(fv_monthly_savings),
                'total_available_corpus': format_inr(total_available_corpus),
                'financial_gap': format_inr(financial_gap),
                'abs_financial_gap': format_inr(abs(financial_gap)),
                'additional_monthly_savings': format_inr(additional_monthly_savings)
            }
        }
    except Exception as e:
        logger.error(f"Error calculating retirement gap: {str(e)}")
        return {'success': False, 'error': str(e)}

def simulate_what_if(baseline_params, scenario_params):
    """
    Simulates a 'What-If' scenario against a baseline profile.
    e.g. 'What happens if I retire at 55 instead of 60?'
         'What happens if I increase monthly savings by ₹10,000?'
         'What happens if my post-retirement expenses drop by 20%?'
    """
    baseline_result = calculate_retirement_gap(baseline_params)
    scenario_result = calculate_retirement_gap(scenario_params)
    
    if not baseline_result.get('success') or not scenario_result.get('success'):
        return {
            'success': False,
            'error': 'Failed to execute What-If simulation.'
        }
        
    b_req = baseline_result['required_corpus']
    s_req = scenario_result['required_corpus']
    b_avail = baseline_result['total_available_corpus']
    s_avail = scenario_result['total_available_corpus']
    b_gap = baseline_result['financial_gap']
    s_gap = scenario_result['financial_gap']
    
    delta_req = s_req - b_req
    delta_avail = s_avail - b_avail
    delta_gap = s_gap - b_gap
    delta_readiness = scenario_result['readiness_percentage'] - baseline_result['readiness_percentage']
    delta_retire_age = scenario_result['retirement_age'] - baseline_result['retirement_age']
    delta_monthly_savings = scenario_result['monthly_savings'] - baseline_result['monthly_savings']
    delta_monthly_expenses = scenario_result['monthly_expenses'] - baseline_result['monthly_expenses']
    
    # Generate tailored actuarial insights based on the scenario difference
    insights = []
    if delta_retire_age < 0:
        years_early = abs(delta_retire_age)
        insights.append(
            f"Retiring {years_early} year(s) earlier (at age {scenario_result['retirement_age']} vs {baseline_result['retirement_age']}) "
            f"cuts your accumulation horizon by {years_early} year(s) and adds {years_early} extra year(s) of retirement living. "
            f"Your projected available nest egg drops by {format_inr(abs(delta_avail))}, widening your shortfall by {format_inr(delta_gap)} (Readiness changes by {delta_readiness:+.1f}%)."
        )
    elif delta_retire_age > 0:
        years_later = delta_retire_age
        insights.append(
            f"Working {years_later} year(s) longer to age {scenario_result['retirement_age']} allows your portfolio to compound {years_later} years more, "
            f"improving your available corpus by {format_inr(delta_avail)} and reducing your required nest egg by {format_inr(abs(delta_req))}."
        )
        
    if delta_monthly_savings > 0:
        insights.append(
            f"Increasing monthly savings by {format_inr(delta_monthly_savings)} boosts your accumulated retirement corpus by {format_inr(delta_avail)}, "
            f"improving readiness by +{delta_readiness:.1f}%."
        )
    elif delta_monthly_savings < 0:
        insights.append(
            f"Reducing monthly savings by {format_inr(abs(delta_monthly_savings))} lowers your final corpus at retirement by {format_inr(abs(delta_avail))}."
        )
        
    if delta_monthly_expenses > 0:
        insights.append(
            f"Higher monthly lifestyle expenses (+{format_inr(delta_monthly_expenses)}) inflate your needed retirement nest egg by {format_inr(delta_req)}."
        )
    elif delta_monthly_expenses < 0:
        insights.append(
            f"Optimizing monthly expenses down by {format_inr(abs(delta_monthly_expenses))} reduces your required retirement corpus by {format_inr(abs(delta_req))}."
        )
        
    if not insights:
        insights.append("No significant parameter changes detected between baseline and scenario.")

    return {
        'success': True,
        'baseline': baseline_result,
        'scenario': scenario_result,
        'deltas': {
            'delta_retire_age': delta_retire_age,
            'delta_monthly_savings': delta_monthly_savings,
            'delta_monthly_expenses': delta_monthly_expenses,
            'delta_required_corpus': delta_req,
            'delta_available_corpus': delta_avail,
            'delta_gap': delta_gap,
            'delta_readiness': round(delta_readiness, 1),
            'formatted': {
                'delta_required_corpus': format_inr(delta_req),
                'delta_available_corpus': format_inr(delta_avail),
                'delta_gap': format_inr(delta_gap)
            }
        },
        'actuarial_insights': insights
    }
