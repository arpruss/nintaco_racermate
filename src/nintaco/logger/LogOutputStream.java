package nintaco.logger;

import java.io.*;
import java.util.logging.*;
import static nintaco.util.StringUtil.*;

// https://blogs.oracle.com/nickstephen/entry/java_redirecting_system_out_and

public class LogOutputStream extends ByteArrayOutputStream {

  private final Logger logger;
  private final Level level;

  public LogOutputStream(final Logger logger, final Level level) {
    this.logger = logger;
    this.level = level;
  }

  @Override
  public void flush() throws IOException {

    final String record;
    synchronized(this) {
      super.flush();
      record = this.toString();
      super.reset();
    }

    if (!isBlank(record)) {
      logger.logp(level, "", "", record);
    }
  }
}
