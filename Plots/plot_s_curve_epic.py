import pandas,pdb,os,sympy,numpy,collections
import matplotlib.pyplot as plt


def solve_scurve(x1,y1,x2,y2):
    x, b1, b2 = sympy.symbols("x b1 b2")    
    res = sympy.solve([sympy.Eq(x1*y1+y1*sympy.exp(b1-(b2*x1))-x1, 0.0),\
                       sympy.Eq(x2*y2+y2*sympy.exp(b1-(b2*x2))-x2, 0.0)], [b1, b2])

    return res

def define_scurve(b1,b2,xvals):
    return xvals/(xvals+numpy.exp(float(b1)-float(b2)*xvals))

epic_cont_vars = collections.OrderedDict([(0,'Root restriction_Coarse Fragment'),(1,'Soil evaporation_Soil Depth'),\
                                          (2,'Harvest index_Growing season'),(3,'Curve number_Soil water'),\
                                          (4,'Soil cover_AGB'),(5,'BD_Rainfall'),(6,'Aeration stress_Soil water'),\
                                          (7,'Plant stress_Nutrient'),(8,'Pest Damage_Weather'),(9,'Harvest index_Water stress'),\
                                          (10,'Water stress_Available water'),(11,''),(12,''),(13,''),\
                                          (14,''),(15,''),(16,''),(17,''),(18,''),(19,''),(20,''),\
                                          (21,''),(22,''),(23,''),(24,''),(25,'')])
{33:'sandtotal_r',51:'silttotal_r',60:'claytotal_r',66:'om_r',\
                  72:'dbthirdbar_r',78:'dbovendry_r',82:'ksat_r',85:'awc_r',\
                  91:'wthirdbar_r',94:'wfifteenbar_r',114:'caco3_r',\
                  126:'cec7_r',132:'sumbases_r',135:'ph1to1h2o_r'}

if __name__ == '__main__':
    x1   = 90.0
    y1   = 0.05
    x2   = 99.0
    y2   = 0.95

    b1, b2 = sympy.symbols("b1 b2")
    res = solve_scurve(x1,y1,x2,y2)

    xvals = numpy.linspace(0,max(x1,x2,100),1000)
    yvals = define_scurve(res.get(b1),res.get(b2),xvals)

    plt.plot(xvals,yvals)
    plt.show()
