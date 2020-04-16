public class Entry {
	private Integer totalScore;
	private Integer topScore;
	private Integer gamesPlayed;
	private String name;
	public Entry(String n, Integer tot, Integer top, Integer g) {
		name = n;
		totalScore = tot;
		topScore = top;
		gamesPlayed = g;
	}
	public Integer getTotal() {
		return totalScore;
	}
	public String getName() {
		return name;
	}
	public Integer getTop() {
		return topScore;
	}
	public Integer getGames() {
		return gamesPlayed;
	}
}