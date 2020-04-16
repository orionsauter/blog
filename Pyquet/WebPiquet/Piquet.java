


public class Piquet {
	public Deck talon;
	public Hand player1;
	public Hand player2;
	public Hand elder;
	public Hand younger;
	public Pile disPile;
	public TrickComp cmp;
	public static final boolean silent = true;
	
	public Piquet() {
		talon = new Deck("Talon");
		player1 = new GeneBotHand("GeneBot");
		player2 = new MemoryBotHand("MemoryBot");
		elder = player1;
		younger = player2;
		player1.setOpponent(player2);
		player2.setOpponent(player1);
		cmp = new TrickComp();	
		disPile = new Pile("Discard");
	}

    public Piquet(GeneBotHand p1, RandBotHand p2) {
		talon = new Deck("Talon");
		player1 = p1;
		player2 = p2;
		elder = player1;
		younger = player2;
		player1.setOpponent(player2);
		player2.setOpponent(player1);
		cmp = new TrickComp();
		disPile = new Pile("Discard");
	}
	
	public void deal(Hand p1, Hand p2) {
		p1.clear();
		p2.clear();
		p1.initUnseen(talon);
		p2.initUnseen(talon);
		if (!silent) System.out.println("Dealing Hands...");
		for (int i = 0; i < 12; i++) {
			p1.addCard(talon.takeTop());
			p2.addCard(talon.takeTop());
		}
	}
	
	public void discard(Hand player, int limit) {
		if (!silent) System.out.println("You may discard up to "+limit+" cards");
		int i = 0;
		for (i = 0; i < limit; i++) {
			if (player.isHuman()) System.out.println("          [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11]");
			if (!silent) System.out.println(player);
			Card c = player.askDiscard();
			if (c == null) break;
			player.removeCard(c);
			disPile.addCard(c);
		}
		for (; i > 0; i--) {
			Card c = talon.takeTop();
			player.addCard(c);
		}
		if (!silent) printStatus(player);
	}
	public void declare() {
		if (!silent) System.out.println("Begining Declarations...");
		// Point
		if (elder.point() > younger.point()) {
			if (!silent) System.out.println("Elder wins point.");
			elder.scorePoint();
		} else if (elder.point() < younger.point()) {
			if (!silent) System.out.println("Younger wins point.");
			younger.scorePoint();
		} else {
			if (!silent) System.out.println("Equal point, no score.");
		}
		// Runs
		if (elder.straight() > younger.straight()) {
			if (!silent) System.out.println("Elder wins runs.");
			elder.scoreStraight();
		} else if (elder.straight() < younger.straight()) {
			if (!silent) System.out.println("Younger wins runs.");
			younger.scoreStraight();
		} else {
			if (!silent) System.out.println("Equal runs, no score.");
		}
		// Tuples
		if (elder.maxTuple() > younger.maxTuple()) {
			if (!silent) System.out.println("Elder wins tuples.");
			elder.scoreTuples();
		} else if (elder.maxTuple() < younger.maxTuple()) {
			if (!silent) System.out.println("Younger wins tuples.");
			younger.scoreTuples();
		} else {
			if (!silent) System.out.println("Equal tuples, no score.");
		}
	}
	
	public void tricks(Hand lead, Hand follow) {
		Hand winner = lead;
		for (int i = 0; i < 12; i++) {
			winner = trickHelper(lead, follow);
			if (winner != lead) {
				Hand tmp = follow;
				follow = lead;
				lead = tmp;
			}
			if (i == 11) {
				if (winner.getTricks() > 6) {
					if (!silent) System.out.println(winner.getName()+" got a capot!");
					winner.addScore(30);
				} else {
					if (!silent) System.out.println(winner.getName()+" won the last trick");
					winner.addScore(1);
					if (lead.getTricks() > 6) {
						if (!silent) System.out.println(lead.getName()+" won the most tricks");
						lead.addScore(10);
					} else if (follow.getTricks() > 6) {
						if (!silent) System.out.println(follow.getName()+" won the most tricks");
						follow.addScore(10);
					}
				}
			}
		}
	}
	
	protected Hand trickHelper(Hand lead, Hand follow) {
		if (lead.isHuman()) System.out.println("          [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11]");
		if (!silent) System.out.println(lead);
		Card leadCard;
		boolean valid = true;
		do {
			valid = true;
			leadCard = lead.askLead();
			if (leadCard == null) {
				valid = false;
				if (lead.isHuman()) System.out.println("No card in that position");
			}
		} while (!valid);
		lead.removeCard(leadCard);
		if (!silent) System.out.println(lead.getName()+" played "+leadCard);
		follow.markSeen(leadCard);
		lead.addScore(1);
		if (follow.isHuman()) System.out.println("          [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11]");
		if (!silent) System.out.println(follow);

		Card followCard;
		do {
			valid = true;
			followCard = follow.askFollow(leadCard);
			if (followCard == null) {
				valid = false;
				if (follow.isHuman()) System.out.println("No card in that position");
			} else if (followCard.getSuit() != leadCard.getSuit() && follow.hasSuit(leadCard.getSuit())) {
				valid = false;
				if (follow.isHuman()) System.out.println("You must follow suit");
			}
		} while (!valid);
		follow.removeCard(followCard);
		if (!silent) System.out.println(follow.getName()+" played "+followCard);
		lead.markSeen(followCard);
		if (cmp.compare(leadCard, followCard) > 0) {
			if (!silent) System.out.println(lead.getName()+" wins trick");
			lead.incTricks();
			return lead;
		} else {
			if (!silent) System.out.println(follow.getName()+" wins trick");
			follow.incTricks();
			follow.addScore(1);
			return follow;
		}
	}
	public int play() {
		while (player1.getScore() < 100 && player2.getScore() < 100) {
			if (!silent) System.out.println("Building Deck...");
			talon.buildDeck(7, 14);
			if (!silent) System.out.println("Shuffling Deck...");
			talon.shuffle();
			deal(player1, player2);
			if (!silent) System.out.println(talon);
			if (!silent) printStatus(elder);
			discard(elder, 5);
			if (!silent) printStatus(younger);
			discard(younger, talon.size());
			declare();
			tricks(elder, younger);
			Hand tmp = elder;
			elder = younger;
			younger = tmp;
		}
		int score = 0;
		if (player1.getScore() >= 100 && player2.getScore() >= 100) {
			if (player1.getScore() > player2.getScore()) {
				if (!silent) System.out.println(player1.getName()+" won with a score of "+(100 + player1.getScore() - player2.getScore()));
				score = (100 + player1.getScore() - player2.getScore());
			} else {
				if (!silent) System.out.println(player2.getName()+" won with a score of "+(100 + player2.getScore() - player1.getScore()));
				score = -1*(100 + player2.getScore() - player1.getScore());
			}
		} else {
			if (player1.getScore() > player2.getScore()) {
				if (!silent) System.out.println(player1.getName()+" won with a score of "+(100 + player1.getScore() + player2.getScore()));
				score = (100 + player1.getScore() + player2.getScore());
			} else {
				if (!silent) System.out.println(player2.getName()+" won with a score of "+(100 + player2.getScore() + player1.getScore()));
				score = -1*(100 + player1.getScore() + player2.getScore());
			}
		}
		player1.clearScore();
		player2.clearScore();
		return score;
	}
	public void printStatus(Hand player) {
		System.out.println(player);
		System.out.println("Point of "+player.point());
		System.out.println("Max Tuple: "+player.tupleLookup(player.maxTuple()));
		System.out.println("Straight: "+player.straightLookup(player.straight()));
		System.out.println("Score: "+player.getScore());
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		Piquet game = new Piquet();
		game.talon.reseed(3);
		for (int i = 0; i < 500; i++) {
			if (i % 2 == 0) {
				game.elder = game.player1;
				game.younger = game.player2;
			} else {
				game.elder = game.player2;
				game.younger = game.player1;
			}
			int score = game.play();
			if (score > 0) {
				System.out.println(score+",0");
			} else {
				System.out.println("0,"+(-1*score));
			}
		}
	}
}
