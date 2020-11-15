"""This code allows generation of more input points for testing, located at regular intervals"""
points_list=[]
xlist=[]
ylist=[]

for i in range(31):
    xlist = xlist + [-1 + i/5]
for i in range(46):
    ylist = ylist + [-1 + i/5]

for i in range(len(xlist)):
    for j in range(len(ylist)):
        points_list=points_list+[(xlist[i], ylist[j])]

more_input = open('more_input.csv', 'w+')

more_input.write('id,x,y')
for i, point in enumerate(points_list):
    more_input.write('\n')
    more_input.write(str(i) + ',' + str(point[0]) + ',' + str(point[1]))
more_input.close()
