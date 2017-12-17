	
import YeeLight as YL
import sys

def scene(presetName):
	light=YL.YeeLight()
	light.connect()
	
	if presetName == "study":
		light.setTemp(3100)
		light.setBright(60)

	if presetName == "night":
	light.setHSV(260,100)
	light.setBright(100)


if __name__="main":
	scene(sys.argv[0])



