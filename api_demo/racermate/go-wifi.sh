python3 exercisebike-wifi.py &
PID=$!
java -jar ../../dist/nintaco.jar -p ../../racermate_r6.nes 
kill $PID
