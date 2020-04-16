import java.util.Random;


public class Deck extends Pile {
	protected static Random rng = new Random();

	public Deck(String n) {
		super(n);
	}

	public Card takeTop() {
		return takeCard(0);
	}
	public void shuffle() {
		int shuffleNum = 20*size();
		for (int i = 0; i < shuffleNum; i++) {
			Card tmp = takeCard(rng.nextInt(size()));
			addCard(tmp);
		}
	}
	public void buildDeck(int minRank, int maxRank) {
		pile.clear();
		for (int i = minRank; i <= maxRank; i++) {
			for (int j = 0; j <= 3; j++) {
				addCard(new Card(i, j));
			}
		}
	}
	public void reseed(int seed) {
		rng.setSeed(seed);
	}
}
