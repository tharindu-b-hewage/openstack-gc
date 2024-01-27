import pandas as pd

df = pd.read_csv('./azure-packing-2020_evictable-probability-distribution.csv')

print('50th quantile', df['perc'].quantile(0.50))
print('60th quantile', df['perc'].quantile(0.60))
print('70th quantile', df['perc'].quantile(0.70))
print('80th quantile', df['perc'].quantile(0.80))
print('90th quantile', df['perc'].quantile(0.90))

# We get the following as below.
# Run 'select COUNT(*) as total, sum( case when vm.priority = 1 then 1 else 0 end ) as evictable, sum( case when vm.priority = 0 then 1 else 0 end ) as reg from vm where vm.starttime > 0;'
# --> total:4699394,evictable:553911,reg:4145483
# divide.
print('alternative: total_evictables / total_requests = ', 0.11786860178142118)

#todo need to implement exact rule as in ds simulator