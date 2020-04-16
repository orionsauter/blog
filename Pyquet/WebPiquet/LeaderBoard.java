import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Scanner;
import java.util.TreeSet;
import java.io.FileNotFoundException;

public class LeaderBoard {
	public String file;
	public static EntryComp cmp;
	private TreeSet<Entry> leader;
	private HashMap<String, Entry> lookup;
	
	LeaderBoard() {
		cmp = new EntryComp();
		lookup = new HashMap<String, Entry>();
		leader = new TreeSet<Entry>(cmp);
	}

	public void setPath(String p) throws FileNotFoundException {
		file = p;
		readFile(file);
	}
	public void readFile(String fileName) throws FileNotFoundException {
		Scanner scanner = new Scanner(new File(fileName));
		while (scanner.hasNext()) {
			String name = scanner.next();
			Integer totScore = scanner.nextInt();
			Integer topScore = scanner.nextInt();
			Integer gamesPlayed = scanner.nextInt();
			Entry e = new Entry(name, totScore, topScore, gamesPlayed);
			leader.add(e);
			lookup.put(name, e);
			scanner.nextLine();
		}
	}

	public TreeSet<Entry> getList() {
		return leader;
	}
	public Entry lookup(String name) {
		return lookup.get(name);
	}
	
	public void update(String name, Integer totScore, Integer topScore) throws IOException {
		Entry ent = lookup(name);
		Integer gamesPlayed = 1;
		if (ent != null) {
			gamesPlayed = ent.getGames() + 1;
			leader.remove(ent);
		}
		ent = new Entry(name, totScore, topScore, gamesPlayed);
		lookup.put(name, ent);
		leader.add(ent);
		FileWriter fstream = new FileWriter(file);
		BufferedWriter out = new BufferedWriter(fstream);
		for (Entry e : leader){
			out.write(e.getName()+" "+e.getTotal()+" "+e.getTop()+" "+e.getGames()+"\n");
		}
		out.flush();
		fstream.flush();
		out.close();
		fstream.close();
	}
}
