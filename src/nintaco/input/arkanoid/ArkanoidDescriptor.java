package nintaco.input.arkanoid;

import net.java.games.input.*;
import nintaco.input.*;
import static net.java.games.input.Component.Identifier.Button.*;

public class ArkanoidDescriptor extends DeviceDescriptor {
  public static final float ARCADE_SPINNER_SCALE = 4.5f;
  
  public static final int Fire = 0;
  
  public static final int RewindTime = 1;

  private static final Component.Identifier.Button[] DEFAULTS = { LEFT, RIGHT };

  private int position = 0x7F;

  private boolean arcadeSpinner = false;
  
  public ArkanoidDescriptor() {
    super(InputDevices.Arkanoid);
  }

  public void setArcadeSpinner(boolean arcadeSpinner) {
    this.arcadeSpinner = arcadeSpinner;
  }

  @Override
  public String getDeviceName() {
    return "Arkanoid Vaus";
  }

  @Override
  public int getButtonCount() {
    return 2;
  }

  @Override
  public int getRewindTimeButton() {
    return RewindTime;
  }

  @Override
  public String getButtonName(final int buttonIndex) {
    switch(buttonIndex) {
      case Fire:
        return "Fire";
      case RewindTime:
        return "Rewind Time";
      default:
        return "Unknown";
    }
  }

  @Override
  public ButtonMapping getDefaultButtonMapping(final int buttonIndex) {
    return getDefaultButtonMapping(InputUtil.getDefaultMouse(), buttonIndex, 
        DEFAULTS);
  }

  @Override
  public int setButtonBits(final int bits, final int consoleType,
      final int portIndex, final int[] pressedValues) {
    
    updateRewindTime(pressedValues[RewindTime] != 0, portIndex);
    
    final int mouseCoordinates;

    if (arcadeSpinner) {
        final int dx = (int)(InputUtil.getMouseDeltaX()/ARCADE_SPINNER_SCALE);
        position += dx;
        if (position < 0)
            position = 0;
        if (position > 240)
            position = 240;
        mouseCoordinates = position;
    }
    else {
        mouseCoordinates = InputUtil.getMouseCoordinates();
    }
    
    int buttons = 0;
    if (mouseCoordinates != 0xFFFF && pressedValues[Fire] != 0) {
      buttons |= 0x04;
    }

    return bits 
        | (mouseCoordinates << 16) 
        | (portIndex == 0 ? buttons : (buttons << 8));    
  }  
}
