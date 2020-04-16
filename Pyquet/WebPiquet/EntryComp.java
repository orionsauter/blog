import java.util.Comparator;


public class EntryComp implements Comparator<Entry> {

	public int compare(Entry e1, Entry e2) {
		float avg1 = e1.getTotal()/e1.getGames();
		float avg2 = e2.getTotal()/e2.getGames();
		if (avg1 < avg2) {
			return 1;
		} else if (avg1 > avg2) {
			return -1;
		} else {
			return 0;
		}
	}

}
