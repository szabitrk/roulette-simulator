from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import xlsxwriter
import matplotlib.pyplot as plt
import time
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# ought to be initialized by the USER
bet = "red"
initialBalance = 25
unit = 0.01
numberOfRounds = 100
output = "RouletteStatistics30.xlsx"
plotName = "RouletteStatistics30.png"

# initializing
print("Initialising..")
s = Service("chromedriver.exe")
driver = webdriver.Chrome(service=s)
driver.get("https://gamdom.com/roulette")

workbook = xlsxwriter.Workbook(output)
worksheet = workbook.add_worksheet()
worksheet.write(0, 0, "Total Rounds: ")
worksheet.write(1, 0, "No. blacks: ")
worksheet.write(2, 0, "No. reds: ")
worksheet.write(3, 0, "No. greens: ")
worksheet.write(5, 0, "Black %:")
worksheet.write(6, 0, "Red %:")
worksheet.write(7, 0, "Green %:")
worksheet.write(16, 0, "One unit:")
worksheet.write(13, 0, "Init Balance:")
worksheet.write(14, 0, "Balance:")
worksheet.write(15, 0, "Profit:")
worksheet.write(10, 0, "No. wins:")
worksheet.write(11, 0, "No. losses:")
worksheet.write(0, 5, "Start time:")
worksheet.write(1, 5, "End time:")

startTime = datetime.now().strftime("%H:%M")
biggestWager = 0
totalWins = 0
totalLosses = 0
balance = initialBalance  # euro
wonLastRound = 0
wager = unit
totalWagered = 0
numList = []
totalRounds = 0
totalRed = 0
totalBlack = 0
totalGreen = 0
redPercent = 0
blackPercent = 0
greenPercent = 0
balanceList = [initialBalance]
roundList = [0]

rouletteTable = {"0": "green",
                 "1": "red", "2": "red", "3": "red", "4": "red", "5": "red", "6": "red", "7": "red",
                 "8": "black", "9": "black", "10": "black", "11": "black", "12": "black", "13": "black", "14": "black"}

for i in range(0, numberOfRounds):
    try:
        # when there is a countdown, bets are possible
        untilStart = WebDriverWait(driver, 25).until(
            ec.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div/div[3]/div[3]/div[1]/div/div[3]/div[2]/div[2]"))
        )
    finally:
        try:
            parentElement = WebDriverWait(driver, 25).until(
                ec.presence_of_element_located((By.CLASS_NAME, "latest_games_links"))
            )
            nums = parentElement.find_elements_by_tag_name("a")
            num = nums[0].text

            totalRounds = totalRounds + 1
            print("Round {} -> Last number was: {} {}".format(i, num, rouletteTable[num]))

            # determining if WIN or LOSE
            if i > 0:
                if rouletteTable[num] == bet:
                    wonLastRound = 1
                    print("You won: {}".format(wager * 2))
                    balance = balance + wager * 2
                    print("Your balance is now: {}".format(balance))
                    totalWins = totalWins + 1
                else:
                    wonLastRound = 0
                    print("You lost: {}".format(wager))
                    print("Your balance is now: {}".format(balance))
                    totalLosses = totalLosses + 1

                print("Win percentage: ", totalWins * 100 / totalRounds)

            balanceList.append(balance)
            roundList.append(i)

            # saving data
            if rouletteTable[num] == "black":
                totalBlack = totalBlack + 1
                blackPercent = totalBlack * 100 / totalRounds
            elif rouletteTable[num] == "red":
                totalRed = totalRed + 1
                redPercent = totalRed * 100 / totalRounds
            else:
                totalGreen = totalGreen + 1
                greenPercent = totalGreen * 100 / totalRounds

            numList.append(nums[0].text)

            # betting
            if i < numberOfRounds:
                if wonLastRound == 0:
                    if i > 0:
                        wager = wager * 2

                    if balance < wager:
                        print("Insufficient funds!")
                        break
                    if rouletteTable[num] != "green":
                        bet = rouletteTable[num]
                else:
                    wager = unit

                if biggestWager < wager:
                    biggestWager = wager

            # printing details
            totalWagered = totalWagered + wager
            balance = balance - wager
            print("------------------------------------------")
            print("You wagered: {} on {}".format(wager, bet))
            print("New balance: [{}] - Total wagered: [{}] - Biggest bet: [{}]".format(balance, totalWagered,
                                                                                       biggestWager))
            print("Game is in progress!")

            # updating data in excel
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()
            worksheet.write(0, 1, totalRounds)
            worksheet.write(1, 1, totalBlack)
            worksheet.write(2, 1, totalRed)
            worksheet.write(3, 1, totalGreen)
            worksheet.write(5, 1, blackPercent)
            worksheet.write(6, 1, redPercent)
            worksheet.write(7, 1, greenPercent)
            profit = balance - initialBalance
            worksheet.write(16, 1, unit)
            worksheet.write(13, 1, initialBalance)
            worksheet.write(14, 1, balance)
            worksheet.write(15, 1, profit)
            worksheet.write(10, 1, totalWins)
            worksheet.write(10, 2, totalWins * 100 / totalRounds)
            worksheet.write(11, 1, totalLosses)
            worksheet.write(11, 2, totalLosses * 100 / totalRounds)
            worksheet.write(0, 6, startTime)
            endTime = datetime.now().strftime("%H:%M")
            worksheet.write(1, 6, endTime)
            workbook.close()

        finally:
            time.sleep(16)

print("Session is over!")
endTime = datetime.now().strftime("%H:%M")

# saving plot
plt.title("Automated Martingale same color pattern system")
plt.xlabel("Rounds")
plt.ylabel("Balance")
plt.plot(roundList, balanceList)
plt.savefig(plotName)

workbook.close()
driver.quit()
