# Simple ROI Model (Kallidus LMS) - Appendix ROI-1

# 1) COSTS (from business report)
# -------------------
year1_cost = 127493.35          # Total Year 1 cost (software + project staff)
year2_cost = 24999.35           # Ongoing licence cost
year3_cost = 24999.35           # Ongoing licence cost

# how Year 1 was built
sandbox_site = 5500.00
additional_licences = 1978.00
kallidus_licences = 24999.35
project_staff = 95016.00
# (These add up to the Year 1 cost)
check_year1 = sandbox_site + additional_licences + kallidus_licences + project_staff

# -------------------
# 2) SAVINGS (from business report)
# -------------------
admin_savings_full = 42000.00    # 2 admin posts removed (full saving)
learning_pool_savings = 10000.00 # Learning Pool contract ended

# Conservative savings in Year 1
# shows a conservative Year 1 saving figure of £26,000
year1_savings_conservative = 26000.00

# Full savings for Years 2 and 3
year2_savings_full = admin_savings_full + learning_pool_savings  # 52000
year3_savings_full = admin_savings_full + learning_pool_savings  # 52000

# -------------------
# 3) CHOOSE SAVINGS SCENARIO
# -------------------
use_conservative_year1 = True

if use_conservative_year1:
    year1_savings = year1_savings_conservative
else:
    year1_savings = admin_savings_full + learning_pool_savings  # 52000

year2_savings = year2_savings_full
year3_savings = year3_savings_full

# -------------------
# 4) NET IMPACT PER YEAR (Savings - Costs)
# -------------------
year1_net = year1_savings - year1_cost
year2_net = year2_savings - year2_cost
year3_net = year3_savings - year3_cost

# -------------------
# 5) CUMULATIVE CASHFLOW (to find break-even)
# -------------------
cumulative = 0.0
cumulative_list = []

for net in [year1_net, year2_net, year3_net]:
    cumulative += net
    cumulative_list.append(cumulative)

# -------------------
# 6) SIMPLE PAYBACK CALCULATION
# -------------------
# If cumulative becomes positive, estimate when it breaks even (roughly)
payback_text = "Not achieved within 3 years"
if cumulative_list[0] >= 0:
    payback_text = "Break-even achieved within Year 1"
elif cumulative_list[1] >= 0:
    # Break-even occurs during Year 2
    amount_left_after_year1 = abs(cumulative_list[0])
    payback_fraction_year2 = amount_left_after_year1 / year2_net
    payback_text = f"Break-even achieved in Year 2 after ~{payback_fraction_year2:.2f} of the year"
elif cumulative_list[2] >= 0:
    # Break-even occurs during Year 3
    amount_left_after_year2 = abs(cumulative_list[1])
    payback_fraction_year3 = amount_left_after_year2 / year3_net
    payback_text = f"Break-even achieved in Year 3 after ~{payback_fraction_year3:.2f} of the year"

# -------------------
# 7) OPTIONAL: 5-YEAR NPV @ 3.5% (simple)
# -------------------
discount_rate = 0.035

# Extend years 4 and 5 assuming ongoing costs and ongoing savings continue
year4_cost = year2_cost
year5_cost = year2_cost
year4_savings = year2_savings
year5_savings = year2_savings

cashflows_5yr = [
    year1_savings - year1_cost,
    year2_savings - year2_cost,
    year3_savings - year3_cost,
    year4_savings - year4_cost,
    year5_savings - year5_cost
]

npv = 0.0
for year_number, cashflow in enumerate(cashflows_5yr, start=1):
    npv += cashflow / ((1 + discount_rate) ** year_number)

# -------------------
# 8) PRINT RESULTS (simple summary)
# -------------------
print("---- SIMPLE ROI SUMMARY (KALLIDUS) ----")
print(f"Year 1 cost check (components): £{check_year1:,.2f} (should match £{year1_cost:,.2f})")
print()

print("Scenario:")
print(" - Conservative Year 1 savings used?" , use_conservative_year1)
print()

print("Net impact (Savings - Costs):")
print(f" Year 1: £{year1_net:,.2f}")
print(f" Year 2: £{year2_net:,.2f}")
print(f" Year 3: £{year3_net:,.2f}")
print()

print("Cumulative net impact:")
print(f" End of Year 1: £{cumulative_list[0]:,.2f}")
print(f" End of Year 2: £{cumulative_list[1]:,.2f}")
print(f" End of Year 3: £{cumulative_list[2]:,.2f}")
print()

print("Payback / Break-even:")
print(" ", payback_text)
print()

print(f"5-Year NPV @ {discount_rate*100:.1f}%: £{npv:,.2f}")
