package nintaco.input.racermate;

import java.io.*;
import nintaco.input.*;
import nintaco.input.icons.*;
import static java.lang.Math.*;
import static nintaco.input.InputDevices.*;
import static nintaco.util.BitUtil.*;
import static nintaco.util.MathUtil.*;

public class RacerMateMapper extends DeviceMapper implements Serializable {
  
  private static final long serialVersionUID = 0;

  private static enum ReceiveType { SPEED, WATTS, PULSE, RPM }; 
  
  private static final float AVERAGE_PEDAL_WEIGHT = 0.0625f;
  private static final float MAX_PEDAL_TIME = 30f;
  private static final float PEDAL_COEFFICIENT = 0.001f;
  
  private static final float WIND_COEFFICIENT = 1f / 99f;
  private static final float DRAG_COEFFICIENT = 0.007f;
  
  private static final float GRADE_COEFFICIENT = 0.0008f / 150f;
  
  private static final float FRICTION_COEFFICIENT = 0.0001f / 140f;
  
  private static final float WATTS_SCALE = 1000f / 140f;
  
  public static final int API_GRADE = 0;
  public static final int API_WIND = 1;
  public static final int API_WEIGHT = 2;
  public static final int API_POWER = 3;
  public static final int API_PULSE = 4;
  public static final int API_RPM = 5;
  public static final int API_SPEED = 6;
  public static final int API_REMOTE_CONTROL = 7;
  public static final int API_NEW_RACE = 8;
  
  private final int shift;
  private final int portIndex;
  
  private int buttons;
  private int out;
  private int writeValue;
  private int readValue;
  private int reads;
  private int readIndex;
  
  private int grade;
  private int wind;
  private int weight;
  
  private boolean remoteControl;
  private int remoteSpeed;
  private int remotePower;
  private int remotePulse;
  private int remoteRPM;
  private boolean newRace = false;
  
  private int pedalTimer = (int)MAX_PEDAL_TIME;
  private float averagePedalTime = MAX_PEDAL_TIME;
  private float speed;
  private boolean leftPedalActive;
  private boolean leftPedalPressed;
  private boolean rightPedalPressed;
  
  private ReceiveType receiveType = ReceiveType.SPEED;

  public RacerMateMapper(final int portIndex) {
    this.shift = portIndex << 3;
    this.portIndex = portIndex;    
    this.remoteControl = false;
  } 
  
  private void write(final int index, int data) {
    switch(index) {
      case 1: // Grade x 10 (-49 to 150)
      case 2: // Wind (-99 to 99)
        if (data >= 0x800) {
          data |= 0xFFFFF000;
        }
        if (index == 1) {
          grade = data;
        } else {
          wind = data;
        }
        break;
      case 3: // Weight (70 to 325)
        weight = data;
        break;
      case 4: // Pulse Target Min (0 to 220)
      case 5: // Pulse Target Max (0 to 220)
        data -= 0x800;
        break;
      case 15: // New race
        if (data == 0x0001)
            newRace = true;
        break;
    }
  }
  
  public int getData(int index) {
      switch(index) {
          case API_GRADE:
            return grade;
          case API_WIND:
            return wind;
          case API_WEIGHT:
            return weight;
          case API_NEW_RACE:
            return newRace ? 1 : 0;
          default:
            return -1;
      }
  }
  
  public void setData(int index, int data) {
      switch(index) {
          case API_SPEED:
            remoteSpeed = data;
            break;
          case API_POWER:
            remotePower = data;
            break;
          case API_PULSE:
            remotePulse = data;
            break;
          case API_RPM:
            remoteRPM = data;
            break;
          case API_REMOTE_CONTROL:
            remoteControl = data != 0;
            break;
          case API_NEW_RACE:
            newRace = data != 0;
      }
      return;
  }
  
  @Override
  public int getInputDevice() {
    return RacerMate1;
  }  
  
  @Override
  public void update(int buttons) {
    
    buttons = (buttons >> shift) & 0xFF;
    
    int keys = buttons & 0x3F;
    if (keys == 0) {
      this.buttons = 0x80; // No buttons pressed is indicated by setting bit 7.
    } else {   
      // Multiple buttons cannot be pressed simultaneously. The loop below
      // finds and applies only the right-most set bit.
      this.buttons = 1;
      while((keys & 1) == 0) { 
        keys >>= 1;
        this.buttons <<= 1;
      }
    }
    
    leftPedalPressed = getBitBool(buttons, 7);
    rightPedalPressed = getBitBool(buttons, 6);
    updateSpeed();
  }
  
  private void updateSpeed() {
    if (remoteControl)
        return;
    
    if (leftPedalActive) {
      if (rightPedalPressed && !leftPedalPressed) {
        leftPedalActive = false;
        pedalTimer = 0;
      } else {
        ++pedalTimer;
      }
    } else {
      if (leftPedalPressed && !rightPedalPressed) {
        leftPedalActive = true;
        pedalTimer = 0;
      } else {
        ++pedalTimer;
      }
    }
    averagePedalTime = AVERAGE_PEDAL_WEIGHT * pedalTimer 
        + (1f - AVERAGE_PEDAL_WEIGHT) * averagePedalTime;
    if (averagePedalTime > MAX_PEDAL_TIME) {
      averagePedalTime = MAX_PEDAL_TIME;
    }
    speed += PEDAL_COEFFICIENT * (1f - averagePedalTime / MAX_PEDAL_TIME);
    
    final float windSpeed = speed + WIND_COEFFICIENT * wind;
    final float drag = DRAG_COEFFICIENT * windSpeed * windSpeed;
    if (windSpeed < 0) {
      speed += drag;
    } else {
      speed -= drag;
    }
    
    speed -= GRADE_COEFFICIENT * grade;
    
    speed -= FRICTION_COEFFICIENT * weight;
    
    if (speed > 1f) {
      speed = 1f;
    } else if (speed < 1E-6f) {
      speed = 0f;
    }
  }
  
  @Override
  public void writePort(final int value) {
    out = value;
  } 
  
  @Override
  public int readPort(final int portIndex) {
        
    if (portIndex == 0) {
      if (reads >= 24 
          && (out == 0xBB || out == 0xEE || out == 0x33 || out == 0xCC)) {  

        reads = 0;        
        if ((out & 1) == 0) {
          
          write(reverseBits((writeValue >> 1) & 0x0F) >> 4, 
              (reverseBits((writeValue >> 5) & 0x7F) << 4) 
                  | (reverseBits((writeValue >> (13 + this.portIndex)) 
                      & 0x1F) >> 3));          
          
          writeValue = readIndex = 0;
          
          switch(receiveType) {
            case SPEED:
              receiveType = ReceiveType.WATTS;
              int rawSpeed = remoteControl ? remoteSpeed : (int)(0xFFF * speed);
              readValue = 0x0100000 | ((rawSpeed) << 8) | buttons;              
              break;
            case WATTS:
              receiveType = ReceiveType.PULSE;
              int rawPower = remoteControl ? remotePower : min(0xFFF, (int)(WATTS_SCALE * speed * weight));
              readValue = 0x0200000 | (rawPower << 8) | buttons;
              break;
            case PULSE:
              receiveType = ReceiveType.RPM;       
              int rawPulse = remoteControl ? remotePulse : clamp((int)(450 * speed), 60, 255);
              readValue = 0x1300000 | (rawPulse << 8) | buttons;
              break;
            case RPM:
              receiveType = ReceiveType.SPEED;
              int rawRPM = remoteControl ? remoteRPM : (int)(0xFF * speed);
              readValue = 0x0680000 | (rawRPM << 8) | buttons;
              break;
          }
          
        } else {
          readIndex = 24;          
        }

        // Player 1 data is delayed by 1 read; player 2 by 2 reads.
        readIndex -= this.portIndex;
        
        return 0;
      } else {
        ++reads;
      }
    }
    
    if (this.portIndex == portIndex) {
      
      int b = (readValue >> (readIndex >> 1)) & 1;
      if ((readIndex & 1) == 0) {
        b ^= 1;
      } 
      
      if (readIndex < 48 && (readIndex & 1) == 1) {
        writeValue = (writeValue << 1) | (out & 1);
      }
      
      ++readIndex;
      
      return b;      
    } else {
      return 0;
    }
  }

  @Override
  public int peekPort(final int portIndex) {
    if (this.portIndex == portIndex) {
      int b = (readValue >> (readIndex >> 1)) & 1;
      if ((readIndex & 1) == 0) {
        b ^= 1;
      }
      return b;      
    } else {
      return 0;
    }
  }  
  
  @Override
  public void render(final int[] screen) {
    final int x = (portIndex == 0) ? 16 : 136;
    final int y = 12;
    InputIcons.RacerMate.render(screen, x, y);
    if (getBitBool(buttons, 0)) {
      InputIcons.RacerMateButton.render(screen, x + 36, y + 32);
    }
    if (getBitBool(buttons, 1)) {
      InputIcons.RacerMateButton.render(screen, x + 36, y + 37);
    }
    if (getBitBool(buttons, 2)) {
      InputIcons.RacerMateButton.render(screen, x + 47, y + 37);
    }
    if (getBitBool(buttons, 3)) {
      InputIcons.RacerMateButton.render(screen, x + 58, y + 32);
    }
    if (getBitBool(buttons, 4)) {
      InputIcons.RacerMateButton.render(screen, x + 47, y + 32);
    }
    if (getBitBool(buttons, 5)) {
      InputIcons.RacerMateButton.render(screen, x + 58, y + 37);
    }    
    if (leftPedalPressed) {
      InputIcons.RacerMateLeftPedal.render(screen, x + 1, y + 15);
    }
    if (rightPedalPressed) {
      InputIcons.RacerMateRightPedal.render(screen, x + 73, y + 15);
    }    
  }  
}
