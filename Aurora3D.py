import matplotlib.pyplot as plt
import sqlite3
from mpl_toolkits.mplot3d.art3d import Line3DCollection

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
    return conn

def main():
    #ToDo: make this more generic
    database = "C:\Aurora151Full\AuroraDB.db"

    conn = create_connection(database)

    #Query all the system names and coordinates
    #ToDo:Check for multiple save games and ask the user which one they want to use. Otherwise they get combined
    sql = """
        With Jump_Details as (
            Select
                A.WarpPointID
                ,A.SystemID
                ,A.WPLink
                ,A.JumpGateStrength
                ,E.Name
                ,E.X
                ,E.Y
                ,E.Z
            From
                FCT_JumpPoint A
            Left Join
                FCT_RaceJUmpPointSurvey B on A.WarpPointID = B.WarpPointID
            Left Join
                FCT_Race C on B.RaceID = C.RaceID
            Left Join
                FCT_System D on A.SystemID = D.SystemID
            Left Join
                Dim_KnownSystems E on D.SystemNumber = E.KnownSystemID
            Where
                C.RaceName = 'Human'
                And B.Explored = 1
            )
        Select Distinct Name,X,Y,Z from Jump_Details      
        """

    cur = conn.cursor()
    cur.execute(sql)

    rows = cur.fetchall()

    #Coordinates for all the systems    
    sName = []
    x = []
    y = []
    z = []

    for row in rows:
        sName.append(row[0])
        x.append(row[1])
        y.append(row[2])
        z.append(row[3])
    
    numRows = len(rows)

    #get the line segments between systems
    sql = """
        With Jump_Details as (
            Select
                A.WarpPointID
                ,A.SystemID
                ,A.WPLink
                ,A.JumpGateStrength
                ,E.Name
                ,E.X
                ,E.Y
                ,E.Z
            From
                FCT_JumpPoint A
            Left Join
                FCT_RaceJUmpPointSurvey B on A.WarpPointID = B.WarpPointID
            Left Join
                FCT_Race C on B.RaceID = C.RaceID
            Left Join
                FCT_System D on A.SystemID = D.SystemID
            Left Join
                Dim_KnownSystems E on D.SystemNumber = E.KnownSystemID
            Where
                C.RaceName = 'Human'
                And B.Explored = 1
            )
        Select 
            A.X as X1,
            A.Y as Y1,
            A.Z as Z1,
            B.X as X2,
            B.Y as Y2,
            B.Z as Z2,
            Case
                When A.JumpGateStrength = 1000 and B.JumpGateStrength = 1000
                    Then 2 --2 way warp gate
                When A.JumpGateStrength = 1000 and B.JumpGateStrength = 0
                    Then 1 --1 way warp gate
                When A.JumpGateStrength = 0 and B.JumpGateStrength = 0
                    Then 0 --no warp gate
                Else
                    "Check your Where clause" --Only count connections once and from the side with a warp gate
            End as GateType
            --,A.Name
            --,B.Name as JumpToName
            --,A.JumpGateStrength
            --,B.JumpGateStrength as ReturnGate
        From 
            Jump_Details A
        Left Join
            Jump_Details B on A.WarpPointID = B.WPLink
        Where
            (A.JumpGateStrength = 1000 and B.JumpGateStrength = 1000 and A.SystemID > B.SystemID)
            or (A.JumpGateStrength = 1000 and B.JumpGateStrength = 0)
            or (A.JumpGateStrength = 0 and B.JumpGateStrength = 0 and A.SystemID > B.SystemID);
        """
    cur.execute(sql)
    res = cur.fetchall()
    conn.close()

    #create list of line segments, eg: [(x1,y1,z1), (x2,y2,z2)], or vectors x,y,z,u,v,w
    segments = [[(seg[0],seg[1],seg[2]),(seg[3],seg[4],seg[5])] for seg in res]

    doubleWarp  = [[(seg[0],seg[1],seg[2]),(seg[3],seg[4],seg[5])] for seg in res if seg[6]==2]
    #singleWarp  = [[(seg[0],seg[1],seg[2],seg[3],seg[4],seg[5])] for seg in res if seg[6]==1]
    noWarp      = [[(seg[0],seg[1],seg[2]),(seg[3],seg[4],seg[5])] for seg in res if seg[6]==0]

    #Create vectors for 1 way warp gates
    x1=[]
    y1=[]
    z1=[]
    u = []
    v = []
    w = []
    
    for seg in res:
        if seg[6]==1:
            x1.append(seg[0])
            y1.append(seg[1])
            z1.append(seg[2])
            u.append(seg[3]-seg[0])
            v.append(seg[4]-seg[1])
            w.append(seg[5]-seg[2])

    #Plot the systems
    fig = plt.figure()
    ax = plt.axes(projection = '3d')

    #create scatter plot
    ax.scatter(x,y,z,c='green', s=200, edgecolors='lime',linewidths =1)

    ax.set_title('Galactic Map') #too much clutter already

    # #plot double warp connections
    lc = Line3DCollection(doubleWarp,colors='orange',linewidths=1)
    ax.add_collection(lc)

    # #plot no warp connections
    lc = Line3DCollection(noWarp,colors='green',linewidths=1)
    ax.add_collection(lc)

    # #plot single warp connections
    ax.quiver(x1,y1,z1,u,v,w,color='deepskyblue',arrow_length_ratio=.1,linewidths=1)

    # lc = Line3DCollection(singleWarp,colors='orange',linewidths=1)
    # ax.add_collection(lc)

    #background
    ax.set_facecolor('midnightblue')#'xkcd:midnightblue')
    plt.axis('off')
    # manager = plt.get_current_fig_manager()
    # manager.resize(*manager.window.maxsize())
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None,hspace=None)

    #add system labels. Labels seems to be the biggest performace drag when rendered
    for i in range(numRows):
        ax.text(x[i],y[i],z[i],sName[i],c='palegoldenrod')

    plt.show()
    
if __name__ == "__main__":
    main()