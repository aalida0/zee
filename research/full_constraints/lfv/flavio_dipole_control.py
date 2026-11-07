import flavio, wilson, particle
from wilson import Wilson
print('versions',flavio.__version__,wilson.__version__,particle.__version__)
print('scale',flavio.config['renormalization scale']['mudecays'])
for name in ['Cgamma_mue','Cgamma_emu']:
 w=Wilson({name: 1e-9+2e-9j},scale=2,eft='WET',basis='flavio')
 a=flavio.np_prediction('BR(mu->egamma)',w)
 b=flavio.np_prediction('BR(mu->eee)',w)
 print(name,a,b,b/a)
