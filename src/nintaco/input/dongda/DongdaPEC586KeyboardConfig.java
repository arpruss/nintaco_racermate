package nintaco.input.dongda;

import java.io.*;
import java.util.*;
import nintaco.input.*;
import static nintaco.input.InputDevices.*;

public class DongdaPEC586KeyboardConfig 
    extends DeviceConfig implements Serializable {
  
  private static final long serialVersionUID = 0;

  public DongdaPEC586KeyboardConfig() {
    super(DongdaPEC586Keyboard);
  }
  
  public DongdaPEC586KeyboardConfig(final List<ButtonMapping> buttonMappings) {
    super(DongdaPEC586Keyboard, buttonMappings);
  }
  
  public DongdaPEC586KeyboardConfig(
      final DongdaPEC586KeyboardConfig dongaPEC586KeyboardConfig) {
    super(dongaPEC586KeyboardConfig);
  }
  
  @Override
  public DongdaPEC586KeyboardConfig copy() {
    return new DongdaPEC586KeyboardConfig(this);
  }  
}