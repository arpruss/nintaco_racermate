package nintaco.gui.image.filters;

import java.awt.image.*;
import java.util.*;

public abstract class VideoFilter {  
  
  private final BufferedImage image;
  protected final int[] out;
  
  public VideoFilter(final BufferedImage image, final int[] out) {
    this.image = image;
    this.out = out;
  }
  
  public VideoFilter(final int scale) {
    image = new BufferedImage(256 * scale, 240 * scale, 
        BufferedImage.TYPE_INT_RGB);
    out = ((DataBufferInt)image.getRaster().getDataBuffer()).getData();
  }
  
  public VideoFilter(final int width, final int height) {
    image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
    out = ((DataBufferInt)image.getRaster().getDataBuffer()).getData();
  }  
  
  public abstract void filter(int[] in, int yFirst, int yLast);
  
  public BufferedImage getImage() {
    return image;
  }

  public int[] getImageData() {
    return out;
  }
  
  public void reset() {
    Arrays.fill(out, 0);
  }
  
  public void dispose() {
    image.flush();
  }
  
  public void setExtendedPalettes(final int[][] extendedPalettes) {    
  }
  
  public void setGhosting(final boolean ghosting) {    
  }
}
