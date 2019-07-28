import tkinter
from tkinter import ttk
import sqlite3
import googlemaps
from operator import itemgetter

# set up connection to SQLite3 db
db_file = "chair.db"
conn1 = sqlite3.connect(db_file)
c1 = conn1.cursor()

db_file = "DataDepot.db"
conn2 = sqlite3.connect(db_file)
c2 = conn2.cursor()

db_file = "PMResults.db"
conn3 = sqlite3.connect(db_file)
c3 = conn3.cursor()


def subnet_list():
    c2.execute("SELECT GatewayIp FROM DTC_FacDB_2 "
              " WHERE GatewayIp IS NOT NULL AND GatewayIp <> '' ORDER BY GatewayIp")
    data = c2.fetchall()
    subnetlist = []
    for row in data:
        subnetlist.append(row[0])
    return subnetlist


def get_data(var):
    parameter = get_clinic_number()
    clear_results()
    preserve, site_address, assigned_group = get_site_info(parameter)
    get_local_techs(parameter, site_address, assigned_group)
    chosenClinic.set("     " + choiceBox.get())
    if preserve != "yes":
        choiceBoxValue.set('')


def get_clinic_number():
    parameter = choiceBox.get()
    c2.execute("SELECT DL_ID FROM DTC_FacDB_2 WHERE GatewayIp='{}'".format(parameter))
    data = c2.fetchone()
    if data is None:
        pass
    else:
        parameter = data[0]
    return parameter


def get_local_techs(parameter, site_address, assigned_group):
    if assigned_group is None or assigned_group == "RRI":
        assigned_group = ""
    else:
        assigned_group = " WHERE AssignedGroup = '" + assigned_group + "'"
    c2.execute("SELECT TechName, AssignedGroup, Notes, Status, Address1, City, State, ZipCode, UserID "
               " FROM User {}".format(assigned_group))
    local_tech_data = c2.fetchall()
    records = tree.get_children()
    for element in records:
        tree.delete(element)
    sorted_tech_list = []
    popup = tkinter.Toplevel()
    tkinter.Label(popup, text="Calculating Google Distances").pack()
    progressbar = ttk.Progressbar(popup, orient='horizontal', length=300, mode='determinate')
    progressbar.pack(side=tkinter.TOP)
    progressbar["maximum"] = len(local_tech_data) * 10
    for item in local_tech_data:
        temp_list = []
        for i in range(len(item)):
            temp_list.append(item[i])
        tech_address = item[4] + " " + item[5] + " " + item[6] + " " + item[7]
        miles, time, distance = get_gmaps_info(site_address, tech_address)
        temp_list.extend([miles, time, distance])
        sorted_tech_list.append(temp_list)
        progressbar.step(10)
        progressbar.update()
    popup.destroy()
    sorted_tech_list = sorted(sorted_tech_list, key=itemgetter(11))
    for item in sorted_tech_list:
        tag = str(item[3])
        tree.insert('', 'end', text=item[0], values=(item[1], item[3], item[9], item[10], item[2]), tags=(tag,))
    c2.execute("SELECT PrefTech FROM PreferredTech WHERE Clinic = '{}'".format(parameter))
    preferred_tech_data = c2.fetchone()
    if preferred_tech_data is None:
        pass
    else:
        prefTechInfo.set(preferred_tech_data[0])


def get_gmaps_info(site_address, tech_address):
    gmaps = googlemaps.Client(key='Insert Google Maps API Key Here')
    my_dist = gmaps.distance_matrix(site_address, tech_address)['rows'][0]['elements'][0]
    if my_dist == {'status': 'ZERO_RESULTS'}:
        distance = 16091830.7
        time = 360059
    else:
        distance = my_dist['distance']['value']
        time = my_dist['duration']['value']
    miles = str(round((distance * 0.000621371), 1))
    time = str(time // 3600) + ':' + str((time % 3600) // 60).zfill(2)
    return miles, time, distance


def get_site_info(parameter):
    c2.execute("SELECT DL_ID,DL_Name, OG_Name, Address1, Address2, City, State, Zip, Type, Status, Phone, GatewayIp, "
              " Fax, Operating_Hours, Station_Count, Mitigation, AssignedGroup FROM DTC_FacDB_2 "
              "WHERE DL_ID = '{}'".format(parameter))
    site_info_data = c2.fetchone()
    if site_info_data is None:
        chosenClinic.set("     Invalid clinic or subnet")
        preserve = "yes"
    else:
        clinicNumber.set(site_info_data[0])
        clinicName.set(site_info_data[1])
        ogName.set(site_info_data[2])
        address1.set(site_info_data[3])
        if site_info_data[4] is None:
            address2.set('')
        else:
            address2.set(site_info_data[4])
        city.set(site_info_data[5])
        state.set(site_info_data[6])
        zipCode.set(site_info_data[7])
        typeInfo.set(site_info_data[8])
        statusInfo.set(site_info_data[9])
        phoneInfo.set(site_info_data[10])
        gatewayIPInfo.set(site_info_data[11])
        faxInfo.set(site_info_data[12])
        operatingHoursInfo.set(site_info_data[13])
        stationsInfo.set(site_info_data[14])
        site_address = site_info_data[3] + " " + site_info_data[5] + " " + site_info_data[6] + " " + site_info_data[7]
        if site_info_data[15] == 1:
            mitigationInfo.set("Yes")
        else:
            mitigationInfo.set("No")
        assigned_group = site_info_data[16]
        try:
            intparameter = int(parameter)
            c1.execute("SELECT TZone FROM Clinic "
                      " WHERE Clinic_ID = '{}'".format(intparameter))
            timezonedata = c1.fetchone()
            try:
                tz = timezonedata[0][8:]
            except TypeError:
                tz = "No timezone info"
            if tz == "Puerto_Rico":
                timezone = "Georgetown, La Paz, Manaus, San Juan"
            elif tz == "New_York":
                timezone = "Eastern Time"
            elif tz == "Detroit":
                timezone = "Eastern Time"
            elif tz == "Indiana/Indianapolis":
                timezone = "Indiana (East)"
            elif tz == "Chicago":
                timezone = "Central Time"
            elif tz == "Denver":
                timezone = "Mountain Time"
            elif tz == "Phoenix":
                timezone = "Arizona"
            elif tz == "Los_Angeles":
                timezone = "Pacific Time"
            elif tz == "Anchorage":
                timezone = "Alaska"
            elif tz == "Honolulu":
                timezone = "Hawaii"
            else:
                timezone = tz
            timezoneInfo.set(timezone)
        except ValueError:
            timezoneInfo.set("No info available")
        c3.execute("SELECT Date, "
                  " Normal_Hours_Start_Monday, Normal_Hours_End_Monday, "
                  " Normal_Hours_Start_Tuesday, Normal_Hours_End_Tuesday, "
                  " Normal_Hours_Start_Wednesday, Normal_Hours_End_Wednesday, "
                  " Normal_Hours_Start_Thursday, Normal_Hours_End_Thursday, "
                  " Normal_Hours_Start_Friday, Normal_Hours_End_Friday, "
                  " Normal_Hours_Start_Saturday, Normal_Hours_End_Saturday, "
                  " Normal_Hours_Start_Sunday, Normal_Hours_End_Sunday "
                  " FROM GoodPMFormsData "
                  " WHERE Clinic_ID = '{}'".format(parameter))
        pm_results_hours_data = c3.fetchall()
        if pm_results_hours_data == []:
            pass
        else:
            pmResultDate.set(pm_results_hours_data[0][0])
            mondayPMHoursInfo.set(pm_results_hours_data[0][1] + " - " + pm_results_hours_data[0][2])
            tuesdayPMHoursInfo.set(pm_results_hours_data[0][3] + " - " + pm_results_hours_data[0][4])
            wednesdayPMHoursInfo.set(pm_results_hours_data[0][5] + " - " + pm_results_hours_data[0][6])
            thursdayPMHoursInfo.set(pm_results_hours_data[0][7] + " - " + pm_results_hours_data[0][8])
            fridayPMHoursInfo.set(pm_results_hours_data[0][9] + " - " + pm_results_hours_data[0][10])
            saturdayPMHoursInfo.set(pm_results_hours_data[0][11] + " - " + pm_results_hours_data[0][12])
            sundayPMHoursInfo.set(pm_results_hours_data[0][13] + " - " + pm_results_hours_data[0][14])
        preserve = "no"
    return preserve, site_address, assigned_group


def clear_results():
    clinicNumber.set('')
    clinicName.set('')
    ogName.set('')
    address1.set('')
    address2.set('')
    city.set('')
    state.set('')
    zipCode.set('')
    typeInfo.set('')
    statusInfo.set('')
    phoneInfo.set('')
    gatewayIPInfo.set('')
    faxInfo.set('')
    operatingHoursInfo.set('')
    stationsInfo.set('')
    mitigationInfo.set('')
    timezoneInfo.set('')
    pmResultDate.set('')
    mondayPMHoursInfo.set('')
    tuesdayPMHoursInfo.set('')
    wednesdayPMHoursInfo.set('')
    thursdayPMHoursInfo.set('')
    fridayPMHoursInfo.set('')
    saturdayPMHoursInfo.set('')
    sundayPMHoursInfo.set('')
    prefTechInfo.set('')


# Tkinter window properties
mainWindow = tkinter.Tk()
mainWindow.title("Google DTC Test")
style = ttk.Style()
style.configure('Treeview.Heading', foreground='black', font=('helvetica', 18))

# Variable declaration
choiceBoxValue = tkinter.Variable(mainWindow)
chosenClinic = tkinter.Variable(mainWindow)
clinicNumber = tkinter.Variable(mainWindow)
clinicName = tkinter.Variable(mainWindow)
ogName = tkinter.Variable(mainWindow)
address1 = tkinter.Variable(mainWindow)
address2 = tkinter.Variable(mainWindow)
city = tkinter.Variable(mainWindow)
state = tkinter.Variable(mainWindow)
zipCode = tkinter.Variable(mainWindow)
typeInfo = tkinter.Variable(mainWindow)
statusInfo = tkinter.Variable(mainWindow)
phoneInfo = tkinter.Variable(mainWindow)
gatewayIPInfo = tkinter.Variable(mainWindow)
faxInfo = tkinter.Variable(mainWindow)
operatingHoursInfo = tkinter.Variable(mainWindow)
stationsInfo = tkinter.Variable(mainWindow)
mitigationInfo = tkinter.Variable(mainWindow)
pmResultDate = tkinter.Variable(mainWindow)
timezoneInfo = tkinter.Variable(mainWindow)
mondayPMHoursInfo = tkinter.Variable(mainWindow)
tuesdayPMHoursInfo = tkinter.Variable(mainWindow)
wednesdayPMHoursInfo = tkinter.Variable(mainWindow)
thursdayPMHoursInfo = tkinter.Variable(mainWindow)
fridayPMHoursInfo = tkinter.Variable(mainWindow)
saturdayPMHoursInfo = tkinter.Variable(mainWindow)
sundayPMHoursInfo = tkinter.Variable(mainWindow)
prefTechInfo = tkinter.Variable(mainWindow)

topFrame = tkinter.Frame(mainWindow)
topFrame.grid(row=0, column=0)
choiceLabel = tkinter.Label(topFrame, text="Enter Clinic ID or Gateway IP:     ")
choiceLabel.grid(row=0, column=0)
choiceBox = ttk.Entry(topFrame, textvariable=choiceBoxValue)   # , values=subnet_list())
choiceBox.grid(row=0, column=1, sticky='ew')
clinicChoice = tkinter.Label(topFrame, textvariable=chosenClinic)
clinicChoice.grid(row=0, column=2)

siteInfoFrame = tkinter.Frame(mainWindow)
siteInfoFrame.grid(row=1, column=0)
# row 0
clinicLabel = tkinter.Label(siteInfoFrame, text="Clinic")
clinicLabel.grid(row=0, column=0)
clinicNumberLabel = tkinter.Entry(siteInfoFrame, textvariable=clinicNumber, justify='center', state='readonly')
clinicNumberLabel.grid(row=0, column=1)
clinicNameLabel = tkinter.Entry(siteInfoFrame, textvariable=clinicName, justify='center', state='readonly')
clinicNameLabel.grid(row=0, column=2, columnspan=5, sticky='ew')
ogLabel = tkinter.Label(siteInfoFrame, text="OG")
ogLabel.grid(row=0, column=7)
ogNameLabel = tkinter.Entry(siteInfoFrame, textvariable=ogName, justify='center', state='readonly')
ogNameLabel.grid(row=0, column=8, columnspan=2, sticky='ew')
# row 1
address1Label = tkinter.Entry(siteInfoFrame, textvariable=address1, justify='center', state='readonly')
address1Label.grid(row=1, column=0, columnspan=3, sticky='ew')
address2Label = tkinter.Entry(siteInfoFrame, textvariable=address2, justify='center', state='readonly')
address2Label.grid(row=1, column=3)
cityLabel = tkinter.Entry(siteInfoFrame, textvariable=city, justify='center', state='readonly')
cityLabel.grid(row=1, column=4, columnspan=3, sticky='ew')
stateLabel = tkinter.Entry(siteInfoFrame, textvariable=state, justify='center', state='readonly')
stateLabel.grid(row=1, column=7)
zipCodeLabel = tkinter.Entry(siteInfoFrame, textvariable=zipCode, justify='center', state='readonly')
zipCodeLabel.grid(row=1, column=8, columnspan=2, sticky='ew')
# row 2
typeLabel = tkinter.Entry(siteInfoFrame, textvariable=typeInfo, justify='center', state='readonly')
typeLabel.grid(row=2, column=0, columnspan=2, sticky='ew')
statusLabel = tkinter.Label(siteInfoFrame, text="Status")
statusLabel.grid(row=2, column=2)
statusInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=statusInfo, justify='center', state='readonly')
statusInfoLabel.grid(row=2, column=3)
phoneLabel = tkinter.Label(siteInfoFrame, text="Phone")
phoneLabel.grid(row=2, column=4)
phoneInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=phoneInfo, justify='center', state='readonly')
phoneInfoLabel.grid(row=2, column=5)
gatewayIPLabel = tkinter.Label(siteInfoFrame, text="Gateway IP")
gatewayIPLabel.grid(row=2, column=6)
gatewayIPInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=gatewayIPInfo, justify='center', state='readonly')
gatewayIPInfoLabel.grid(row=2, column=7)
faxLabel = tkinter.Label(siteInfoFrame, text="Fax")
faxLabel.grid(row=2, column=8)
faxInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=faxInfo, justify='center', state='readonly')
faxInfoLabel.grid(row=2, column=9)
# row 3
operatingHoursLabel = tkinter.Label(siteInfoFrame, text="Operating Hours")
operatingHoursLabel.grid(row=3, column=0, columnspan=2)
operatingHoursInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=operatingHoursInfo, justify='center',
                                        state='readonly')
operatingHoursInfoLabel.grid(row=3, column=2, columnspan=4, sticky='ew')
stationsLabel = tkinter.Label(siteInfoFrame, text="Stations")
stationsLabel.grid(row=3, column=6)
stationsInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=stationsInfo, justify='center', state='readonly')
stationsInfoLabel.grid(row=3, column=7)
mitigationLabel = tkinter.Label(siteInfoFrame, text="Mitigation")
mitigationLabel.grid(row=3, column=8)
mitigationInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=mitigationInfo, justify='center', state='readonly')
mitigationInfoLabel.grid(row=3, column=9)
# row 4
pmResultLabel = tkinter.Label(siteInfoFrame, text="PM Results Hours as of:")
pmResultLabel.grid(row=4, column=0)
mondayPMHoursLabel = tkinter.Label(siteInfoFrame, text="Monday")
mondayPMHoursLabel.grid(row=4, column=3)
tuesdayPMHoursLabel = tkinter.Label(siteInfoFrame, text="Tuesday")
tuesdayPMHoursLabel.grid(row=4, column=4)
wednesdayPMHoursLabel = tkinter.Label(siteInfoFrame, text="Wednesday")
wednesdayPMHoursLabel.grid(row=4, column=5)
thursdayPMHoursLabel = tkinter.Label(siteInfoFrame, text="Thursday")
thursdayPMHoursLabel.grid(row=4, column=6)
fridayPMHoursLabel = tkinter.Label(siteInfoFrame, text="Friday")
fridayPMHoursLabel.grid(row=4, column=7)
saturdayPMHoursLabel = tkinter.Label(siteInfoFrame, text="Saturday")
saturdayPMHoursLabel.grid(row=4, column=8)
sundayPMHoursLabel = tkinter.Label(siteInfoFrame, text="Sunday")
sundayPMHoursLabel.grid(row=4, column=9)
# row 5
pmResultDateLabel = tkinter.Entry(siteInfoFrame, textvariable=pmResultDate, justify='center', state='readonly')
pmResultDateLabel.grid(row=5, column=0)
timezoneLabel = tkinter.Label(siteInfoFrame, text="Time Zone")
timezoneLabel.grid(row=5, column=1)
timezoneInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=timezoneInfo, justify='center', state='readonly')
timezoneInfoLabel.grid(row=5, column=2)
mondayPMHoursInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=mondayPMHoursInfo, justify='center',
                                       state='readonly')
mondayPMHoursInfoLabel.grid(row=5, column=3)
tuesdayPMHoursInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=tuesdayPMHoursInfo, justify='center',
                                        state='readonly')
tuesdayPMHoursInfoLabel.grid(row=5, column=4)
wednesdayPMHoursInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=wednesdayPMHoursInfo, justify='center',
                                          state='readonly')
wednesdayPMHoursInfoLabel.grid(row=5, column=5)
thursdayPMHoursInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=thursdayPMHoursInfo, justify='center',
                                         state='readonly')
thursdayPMHoursInfoLabel.grid(row=5, column=6)
fridayPMHoursInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=fridayPMHoursInfo, justify='center',
                                       state='readonly')
fridayPMHoursInfoLabel.grid(row=5, column=7)
saturdayPMHoursInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=saturdayPMHoursInfo, justify='center',
                                         state='readonly')
saturdayPMHoursInfoLabel.grid(row=5, column=8)
sundayPMHoursInfoLabel = tkinter.Entry(siteInfoFrame, textvariable=sundayPMHoursInfo, justify='center',
                                       state='readonly')
sundayPMHoursInfoLabel.grid(row=5, column=9)
# row 6
spacerLabel = tkinter.Label(siteInfoFrame, text="").grid(row=6, column=0, columnspan=9)

bottomFrame = tkinter.Frame(mainWindow)
bottomFrame.grid(row=2, column=0)
prefTechLabel = tkinter.Label(bottomFrame, text="Preferred Tech").grid(row=0, column=0)
prefTechInfoLabel = tkinter.Entry(bottomFrame, textvariable=prefTechInfo, justify='center', state='readonly')
prefTechInfoLabel.grid(row=0, column=1)
tree = ttk.Treeview(bottomFrame, height=18, column=['', '', '', '', ''], style='Treeview.Heading')
tree.column('#0', width=150)
tree.column('#1', width=200)
tree.column('#2', width=80)
tree.column('#3', width=80)
tree.column('#4', width=80)
tree.column('#5', width=200)
tree.grid(row=1, column=0, columnspan=3)
tree.heading('#0', text='Tech Name')
tree.heading('#1', text='Assigned Group')
tree.heading('#2', text='Status')
tree.heading('#3', text='Distance')
tree.heading('#4', text='Time(hh:mm)')
tree.heading('#5', text='Notes')
tree.tag_configure("In", background='#90EE90', font=('helvetica', 10))
tree.tag_configure('Out', background='#FF6666', font=('helvetica', 10))
tree.tag_configure('Unavailable', background='#FFFF99', font=('helvetica', 10))

choiceBox.focus()
# choiceBox.bind("<<ComboboxSelected>>", get_data)
choiceBox.bind("<Return>", get_data)

# mainWindow.iconbitmap('warning.ico')

mainWindow.mainloop()
