import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;

/**
 * Writes the ten digit images used by the 1% battery icons.
 *
 * Each digit is drawn white on a transparent background with a dark 1 px
 * outline, in the 5x9 pixel font below ("1" is 3 px wide). Image size is
 * (glyph width + 2) x 11. The images go into the slots of the 5%-step
 * battery pictures (stat_sys_battery_5.png holds "0", _15 holds "1", ...,
 * _95 holds "9"). The level-lists written by make_xml.py no longer use those
 * pictures as batteries.
 *
 * usage: java MakeDigits <output dir>
 */
public class MakeDigits {
    static final String[][] FONT = {
        {".###.", "##.##", "##.##", "##.##", "##.##", "##.##", "##.##", "##.##", ".###."}, // 0
        {".##", "###", ".##", ".##", ".##", ".##", ".##", ".##", ".##"},                   // 1
        {".###.", "##.##", "...##", "...##", "..##.", ".##..", "##...", "##...", "#####"}, // 2
        {"####.", "...##", "...##", "...##", ".###.", "...##", "...##", "...##", "####."}, // 3
        {"...##", "..###", ".#.##", "#..##", "#####", "...##", "...##", "...##", "...##"}, // 4
        {"#####", "##...", "##...", "####.", "...##", "...##", "...##", "##.##", ".###."}, // 5
        {".###.", "##...", "##...", "####.", "##.##", "##.##", "##.##", "##.##", ".###."}, // 6
        {"#####", "...##", "...##", "..##.", "..##.", ".##..", ".##..", ".##..", ".##.."}, // 7
        {".###.", "##.##", "##.##", "##.##", ".###.", "##.##", "##.##", "##.##", ".###."}, // 8
        {".###.", "##.##", "##.##", "##.##", ".####", "...##", "...##", "...##", ".###."}, // 9
    };
    static final int TEXT = 0xFFFFFFFF, OUTLINE = 0xE0000000;

    public static void main(String[] args) throws Exception {
        File out = new File(args[0]);
        out.mkdirs();
        for (int d = 0; d <= 9; d++) {
            String[] g = FONT[d];
            int w = g[0].length() + 2, h = g.length + 2;
            BufferedImage img = new BufferedImage(w, h, BufferedImage.TYPE_INT_ARGB);
            for (int y = 0; y < h; y++)
                for (int x = 0; x < w; x++) {
                    if (ink(g, x - 1, y - 1)) {
                        img.setRGB(x, y, TEXT);
                        continue;
                    }
                    boolean near = false;
                    for (int dy = -1; dy <= 1; dy++)
                        for (int dx = -1; dx <= 1; dx++)
                            near |= ink(g, x - 1 + dx, y - 1 + dy);
                    img.setRGB(x, y, near ? OUTLINE : 0);
                }
            String name = "stat_sys_battery_" + (10 * d + 5) + ".png";
            if (!ImageIO.write(img, "png", new File(out, name))) throw new Exception("no PNG writer");
        }
    }

    private static boolean ink(String[] g, int x, int y) {
        return y >= 0 && y < g.length && x >= 0 && x < g[y].length() && g[y].charAt(x) == '#';
    }
}
