import java.io.*;
import java.util.ArrayList;

import javax.servlet.*;
import javax.servlet.http.*;

@SuppressWarnings("serial")
public class WebPiquetGame extends HttpServlet {
	public Deck talon;
	public Hand player1;
	public Hand player2;
	public Hand elder;
	public Hand younger;
	public Hand lead;
	public Hand follow;
	public Pile disPile;
	public TrickComp cmp;
	public PrintWriter out;
	public int gameState = 0;
	public ArrayList<Card> dis;
	public int disNum;
	public String buffer;
	public int trickNum;
	public Card leadCard;
	public Card followCard;
	public String inputString;
	public Integer input;
	public boolean repique;
	public boolean gameOver = false;
	public boolean watch;
	public int finalScore;
	
	public WebPiquetGame(String name) {
		talon = new Deck("Talon");
		player1 = new Hand(name);
		player2 = new RandBotHand("RandBot");
		elder = lead = player1;
		younger = follow = player2;
		cmp = new TrickComp();	
		disPile = new Pile("Discard");
		dis = new ArrayList<Card>();
		trickNum = 0;
		finalScore = 0;
    	watch = false;
	}
	
	public void deal(Hand p1, Hand p2) {
		p1.clear();
		p2.clear();
		p1.initUnseen(talon);
		p2.initUnseen(talon);
		for (int i = 0; i < 12; i++) {
			p1.addCard(talon.takeTop());
			p2.addCard(talon.takeTop());
		}
	}
	
	public void discard(Hand player, int limit) {
		int i = 0;
		for (i = 0; i < limit; i++) {
			Card c = player.askDiscard();
			if (c == null) break;
			player.removeCard(c);
			disPile.addCard(c);
		}
		for (; i > 0; i--) {
			Card c = talon.takeTop();
			player.addCard(c);
		}
	}
	public void declare() {
		out.println("Begining Declarations...<br>");
		// Point
		if (elder.point() > younger.point()) {
			out.println(elder.getName()+" wins with a point of "+elder.point()+".  "+younger.getName()+" had a point of "+younger.point()+".<br>");
			elder.scorePoint();
		} else if (elder.point() < younger.point()) {
			out.println(younger.getName()+" wins with a point of "+younger.point()+".  "+elder.getName()+" had a point of "+elder.point()+".<br>");
			younger.scorePoint();
		} else {
			out.println("Equal point, no score.<br>");
		}
		checkRepique();
		// Runs
		if (elder.straight() > younger.straight() && elder.straight() > 50) {
			out.println(elder.getName()+" wins with a "+elder.straightLookup(elder.straight())+".  "+younger.getName()+" had a "+younger.straightLookup(younger.straight())+".<br>");
			elder.scoreStraight();
		} else if (elder.straight() < younger.straight() && younger.straight() > 50) {
			out.println(younger.getName()+" wins with a "+younger.straightLookup(younger.straight())+".  "+elder.getName()+" had a "+elder.straightLookup(elder.straight())+".<br>");
			younger.scoreStraight();
		} else {
			out.println("Equal runs, no score.<br>");
		}
		checkRepique();
		// Tuples
		if (elder.maxTuple() > younger.maxTuple()) {
			out.println(elder.getName()+" wins with a "+elder.tupleLookup(elder.maxTuple())+".  "+younger.getName()+" had a "+younger.tupleLookup(younger.maxTuple())+".<br>");
			elder.scoreTuples();
		} else if (elder.maxTuple() < younger.maxTuple()) {
			out.println(younger.getName()+" wins with a "+younger.tupleLookup(younger.maxTuple())+".  "+elder.getName()+" had a "+elder.tupleLookup(elder.maxTuple())+".<br>");
			younger.scoreTuples();
		} else {
			out.println("Equal tuples, no score.<br>");
		}
		checkRepique();
	}
	public void checkRepique() {
		if (player1.getScore() > 30 && player2.getScore() == 0 && !repique) {
			out.println(player1.getName()+" got a repique!<br>");
			player1.addScore(60);
			repique = true;
		} else if (player2.getScore() > 30 && player1.getScore() == 0 && !repique) {
			out.println(player2.getName()+" got a repique!<br>");
			player2.addScore(60);
			repique = true;
		}
	}
	public void checkPique() {
		if (player1.getScore() > 30 && player2.getScore() == 0 && !repique) {
			buffer += (player1.getName()+" got a pique!<br>");
			player1.addScore(30);
			repique = true;
		} else if (player2.getScore() > 30 && player1.getScore() == 0 && !repique) {
			buffer += (player2.getName()+" got a pique!<br>");
			player2.addScore(30);
			repique = true;
		}
	}
	public void setWriter(PrintWriter w) { out = w; }
	public void printOpp() {
		out.println("<p align=\"center\">Opponent</p>");
		out.println("<p align=\"center\">");
		if (watch) {
			for (int i = 0; i < player2.size(); i++) {
				out.println("  <img name=\"card\" src=\"../cards/"+player2.getIndex(i)+".png\" width=71 height=\"96\" >");
			}
		} else {
			for (int i = 0; i < player2.size(); i++) {
				out.println("  <img name=\"card\" src=\"../cards/b1fv.png\" width=71 height=\"96\" >");
			}
		}
		for (int i = 0; i < 12 - player2.size(); i++) {
			out.println("  <img name=\"card\" src=\"../cards/empty.png\" width=71 height=\"96\" >");
		}
		out.println("</p>");
	}
	public void printTalon() {
		out.println("<p align=\"center\">");
		for (int i = 0; i < talon.size(); i++) {
			out.println("  <img name=\"card\" src=\"../cards/b1fv.png\" width=71 height=\"96\" >");
		}
		for (int i = 0; i < 8 - talon.size(); i++) {
			out.println("  <img name=\"card\" src=\"../cards/empty.png\" width=71 height=\"96\" >");
		}
		out.println("</p>");
	}
	public void printPlayer() {
		out.println("<p align=\"center\">");
		for (int i = 0; i < player1.size(); i++) {
			out.println("  <a href=\"WebPiquet?c="+i+"\"><img src=\"../cards/"+player1.getIndex(i)+".png\"  name=\"card\" width=\"71\" height=\"96\" border=\"0\"></a>");
		}
		for (int i = 0; i < 12 - player1.size(); i++) {
			out.println("  <img name=\"card\" src=\"../cards/empty.png\" width=71 height=\"96\" >");
		}
		out.println("</p>");
	}
	public void printTable() {
		out.println("<div align=\"center\">");
		out.println("  <p>You</p>");
		out.println("  <table width=\"300\" border=\"1\">");
		out.println("    <tr>");
		out.println("      <td> Your Score</td>");
		out.println("      <td>"+player1.getScore()+"</td>");
		out.println("    </tr>");
		out.println("    <tr>");
		out.println("      <td>Opponent's Score </td>");
		out.println("      <td>"+player2.getScore()+"</td>");
		out.println("    </tr>");
		out.println("    <tr>");
		if (gameState > 60) {
			out.println("      <td>Tricks Won</td>");
			out.println("      <td>"+player1.getTricks()+"</td>");
			out.println("    </tr>");
			out.println("    <tr>");
		} else {
			out.println("      <td>Point</td>");
			out.println("      <td>"+player1.point()+"</td>");
			out.println("    </tr>");
			out.println("    <tr>");
			out.println("      <td>Highest Tuple </td>");
			out.println("      <td>"+player1.tupleLookup(player1.maxTuple())+"</td>");
			out.println("    </tr>");
			out.println("    <tr>");
			out.println("      <td>Highest Straight</td>");
			out.println("      <td>"+player1.straightLookup(player1.straight())+"</td>");
			out.println("    </tr>");
			out.println("  </table>");
			out.println("  <p>&nbsp;</p>");
			out.println("</div>");
		}
	}
	
	public void printDecl() {
		declare();
	}
	public void printTricks() {
		//out.println("<p align=\"center\">");
		if (gameState < 90) {
			out.println("  <img name=\"card\" src=\"../cards/empty.png\" width=71 height=\"96\" >");
			out.println("  <img name=\"card\" src=\"../cards/empty.png\" width=71 height=\"96\" ><br><br>");
		} else if (gameState < 110) {
			out.println("  <img name=\"card\" src=\"../cards/"+leadCard+".png\" width=71 height=\"96\" >");
			out.println("  <img name=\"card\" src=\"../cards/empty.png\" width=71 height=\"96\" ><br><br>");
		} else if (gameState == 110) {
			out.println("  <img name=\"card\" src=\"../cards/"+leadCard+".png\" width=71 height=\"96\" >");
			out.println("  <img name=\"card\" src=\"../cards/"+followCard+".png\" width=71 height=\"96\" ><br><br>");
			lead.markSeen(followCard);
		} else if (gameState == 120) {
			out.println("  <img name=\"card\" src=\"../cards/"+leadCard+".png\" width=71 height=\"96\" >");
			out.println("  <img name=\"card\" src=\"../cards/"+followCard+".png\" width=71 height=\"96\" ><br>");
			buffer += lead.getName()+" won the trick.<br>";
			checkPique();
		} else if (gameState == 130) {
			if (lead.getTricks() > 6) {
				out.println(lead.getName()+" got a capot!<br>");
				lead.addScore(30);
			} else {
				out.println(lead.getName()+" won the last trick<br>");
				lead.addScore(1);
				if (lead.getTricks() > 6) {
					out.println(lead.getName()+" won the most tricks<br>");
					lead.addScore(10);
				} else if (follow.getTricks() > 6) {
					out.println(follow.getName()+" won the most tricks<br>");
					follow.addScore(10);
				}
			}
		}
		//out.println("</p>");
	}
	public void printFinal() {
		if (player1.getScore() > 99 && player2.getScore() > 99) {
			if (player1.getScore() > player2.getScore()) {
				out.println(player1.getName()+" won with a score of "+(100 + player1.getScore() - player2.getScore())+"<br>");
				finalScore = (100 + player1.getScore() - player2.getScore());
			} else {
				out.println(player2.getName()+" won with a score of "+(100 + player2.getScore() - player1.getScore())+"<br>");
				finalScore = -1*(100 + player1.getScore() - player2.getScore());
			}
		} else {
			if (player1.getScore() > player2.getScore()) {
				out.println(player1.getName()+" won with a score of "+(100 + player1.getScore() + player2.getScore())+"<br>");
				finalScore = (100 + player1.getScore() + player2.getScore());
			} else {
				out.println(player2.getName()+" won with a score of "+(100 + player2.getScore() + player1.getScore())+"<br>");
				finalScore = -1*(100 + player1.getScore() + player2.getScore());
			}
		}
	}
	public void printStatus() {
		out.println("<DIV id=\"header\">");
		printOpp();
		out.println("<hr></DIV><DIV id=\"main\"><p align=\"center\">");
		if (gameState < 60) {
			//printTalon();
		} else if (gameState == 60) {
			printDecl();
		} else if (gameState < 140) {
			printTricks();
		} else {
			printFinal();
		}
		out.println(buffer);
		out.println("</p></DIV><DIV id=\"footer\"><hr>");
		printPlayer();
		printTable();
		out.println("</DIV>");
	}
	
	public void refresh() {
		buffer += ("<a href=\"WebPiquet?c=12\">Click Here to Continue</a><br>");
	}
	
	public int getFinalScore() {
		return finalScore;
	}
	
	public void doGet(HttpServletRequest request, HttpServletResponse response)
    throws IOException, ServletException
    {
		buffer = "";
		response.setContentType("text/html");
		setWriter(response.getWriter());
        out.println("<html>");
        out.println("<head>");
        out.println("<title>WebPiquet</title>");
        out.println("<STYLE type=\"text/css\" media=\"screen\">");
        out.println(" BODY { height: 6in }");
        out.println("  #header {");
        out.println("    position: fixed;");
        out.println("    width: 100%;");
        out.println("    height: 23%;");
        out.println("     top: 0;");
        out.println("     right: 0;");
        out.println("     bottom: auto;");
        out.println("     left: 0;");
        out.println("  }");
        out.println("  #main {");
        out.println("    position: fixed;");
        out.println("    width: 100%;");
        out.println("    height: 34%;");
        out.println("    top: 30%;");
        out.println("    right: 0;");
        out.println("    bottom: auto;");
        out.println("    left: 0;");
        out.println("  }");
        out.println("  #footer {");
        out.println("   position: fixed;");
        out.println("    width: 100%;");
        out.println("    height: 40%;");
        out.println("    top: auto;");
        out.println("   right: 0;");
        out.println("   bottom: 0;");
        out.println("    left: 0;");
        out.println("  }");
        out.println(" </STYLE>");
        out.println(" </HEAD>");
        out.println("<body>");
        
        switch (gameState) {
        case 0: // Intro Screen
        	out.println("<p align=\"center\"><h1>Welcome to WebPiquet</h1><br>");
        	out.print("You are logged in as "+player1.getName());
        	gameState = 10;
        	out.print("<form action=\"");
            out.print("WebPiquet\" ");
            out.println("method=POST>");
            
            out.println("Choose an opponent:<br>");
            out.println("<input type=radio name=opp value=0>");
            out.println("<b>RandBot</b><br>");
            out.println("Discard: Random card<br>");
            out.println("Lead: Random card<br>");
            out.println("Follow: Random card<br><br>");
            
            out.println("<input type=radio name=opp value=1>");
            out.println("<b>MinRandBot</b><br>");
            out.println("Discard: Minimum card<br>");
            out.println("Lead: Random card<br>");
            out.println("Follow: Random card<br><br>");
            
            out.println("<input type=radio name=opp value=2>");
            out.println("<b>MinMaxBot</b><br>");
            out.println("Discard: Minimum card<br>");
            out.println("Lead: Maximum card<br>");
            out.println("Follow: Maximum card<br><br>");
            
            out.println("<input type=radio name=opp value=3>");
            out.println("<b>MinMaxMinBot</b><br>");
            out.println("Discard: Minimum card<br>");
            out.println("Lead: Maximum card<br>");
            out.println("Follow: Minimum card<br><br>");
            
            out.println("<input type=radio name=opp value=4>");
            out.println("<b>RunBot v2</b><br>");
            out.println("Discard: Minimum card<br>");
            out.println("Lead: Maximum card in previously led suit<br>");
            out.println("Follow: Minimum card to beat lead if possible, else minimum card<br><br>");
            
            out.println("<input type=radio name=opp value=5>");
            out.println("<b>MemoryBot v3</b><br>");
            out.println("Discard: Minimum card unless needed for straight or tuple<br>");
            out.println("Lead: Maximum card if has at least two winning cards in suit, else minimum card<br>");
            out.println("Follow: Minimum card to beat lead if possible, else minimum card<br><br>");
            
            out.println("<input type=radio name=opp value=6>");
            out.println("<b>PermBot</b><br>");
            out.println("Discard: Minimum card unless needed for straight or tuple<br>");
            out.println("Lead & Follow: Card that maximizes winning outcomes in next three tricks<br>");
            out.println("Note: PermBot is a thoughtful player. Plotting the game tree takes time.<br><br>");
            
            watch = false;
            out.println("<input type=checkbox name=watch> Watch opponent's hand (no score recorded)<br>");
            
            out.print("<input type=submit value=\"");
            out.print("Begin\">");
            out.println("</form></p>");
            break;
        case 10:  // Begin Game
        	gameState = 15;
        	elder = lead = player1;
        	younger = follow = null;
        	inputString = request.getParameter("opp");
        	if (inputString != null) {
        		input = Integer.parseInt(inputString);
        		if (input == 0) {
        			younger = follow = player2 = new RandBotHand("RandBot");
        		} else if (input == 1) {
        			younger = follow = player2 = new MinBotHand("MinRandBot");
        		} else if (input == 2) {
        			younger = follow = player2 = new MinMaxBotHand("MinMaxBot");
        		} else if (input == 3) {
        			younger = follow = player2 = new MinMaxMinBotHand("MinMaxMinBot");
        		} else if (input == 4) {
        			younger = follow = player2 = new RunBotHand("RunBot");
        		} else if (input == 5) {
        			younger = follow = player2 = new MemoryBotHand("MemoryBot");
        		} else if (input == 6) {
        			younger = follow = player2 = new PermBotHand("PermBot");
        		} else {
        			younger = follow = player2 = new RandBotHand("RandBot");
        		}
        	} else {
        		gameState = 0;
            	System.out.println("<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">");
        	}
        	if ("on".equals(request.getParameter("watch"))) watch = true;
        case 15:
        	talon.buildDeck(7, 14);
        	talon.shuffle();
        	deal(player1, player2);
        	repique = false;
        	gameState = 20;
        case 20: // Elder Discard
        	if (elder.isHuman()) {
        		inputString = request.getParameter("c");
        		if (inputString != null) {
        			input = Integer.parseInt(inputString);
        		} else {
        			input = null;
        		}
        		if (input == null) {
        			dis.clear();
        			buffer += ("Choose card to discard<br>");
        			buffer += ("<a href=\"WebPiquet?c=12\">When finished discarding, click here</a><br>");
        			buffer += ("Discarded so far:<br>");
        			for (int i = 0; i < dis.size(); i++) {
        				buffer += ("  <img name=\"card\" src=\"../cards/"+dis.get(i)+".png\" width=71 height=\"96\" >");
        			}
        			for (int i = 0; i < 5 - dis.size(); i++) {
        				buffer += ("  <img name=\"card\" src=\"../cards/empty.png\" width=71 height=\"96\" >");
        			}
        		} else if (input < 12) {
        			Card c = elder.removeIndex(input);
        			dis.add(c);
        			buffer += ("Choose a card to discard<br>");
        			buffer += ("<a href=\"WebPiquet?c=12\">When finished discarding, click here</a><br>");
        			buffer += ("Discarded so far:<br>");
        			for (int i = 0; i < dis.size(); i++) {
        				buffer += ("  <img name=\"card\" src=\"../cards/"+dis.get(i)+".png\" width=71 height=\"96\" >");
        			}
        			for (int i = 0; i < 5 - dis.size(); i++) {
        				buffer += ("  <img name=\"card\" src=\"../cards/empty.png\" width=71 height=\"96\" >");
        			}
        			if (dis.size() == 5) gameState = 30; // Reached limit
        		} else {
        			gameState = 30;
                	buffer += "<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">";
        		}
        		break;
        	} else {
        		discard(elder, 5);
        		gameState = 40;
            	buffer += "<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">";
        	}
        	break;
        case 30: // Elder Discard Human
        	gameState = 40;
        	while (elder.size() < 12) {
        		elder.addCard(talon.takeTop());
        	}
        	buffer += "<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">";
        	break;
        case 40: // Younger Discard
        	if (younger.isHuman()) {
        		inputString = request.getParameter("c");
        		if (inputString != null) {
        			input = Integer.parseInt(inputString);
        		} else {
        			input = null;
        		}
        		if (input == null) {
            		dis.clear();
        			buffer += ("Choose card to discard<br>");
        			buffer += ("<a href=\"WebPiquet?c=12\">When finished discarding, click here</a><br>");
        			buffer += ("Discarded so far:<br>");
        			for (int i = 0; i < dis.size(); i++) {
        				buffer += ("  <img name=\"card\" src=\"../cards/"+dis.get(i)+".png\" width=71 height=\"96\" >");
        			}
        			for (int i = 0; i < talon.size() - dis.size(); i++) {
        				buffer += ("  <img name=\"card\" src=\"../cards/empty.png\" width=71 height=\"96\" >");
        			}
        		} else if (input < 12) {
        			Card c = younger.removeIndex(input);
        			dis.add(c);
        			buffer += ("Choose card to discard<br>");
        			buffer += ("<a href=\"WebPiquet?c=12\">When finished discarding, click here</a><br>");
        			buffer += ("Discarded so far:<br>");
        			for (int i = 0; i < dis.size(); i++) {
        				buffer += ("  <img name=\"card\" src=\"../cards/"+dis.get(i)+".png\" width=71 height=\"96\" >");
        			}
        			for (int i = 0; i < talon.size() - dis.size(); i++) {
        				buffer += ("  <img name=\"card\" src=\"../cards/empty.png\" width=71 height=\"96\" >");
        			}
        			if (dis.size() == talon.size()) gameState = 50; // Reached limit
        		} else {
        			gameState = 50;
                	buffer += "<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">";
        		}
        		break;
        	} else {
        		discard(younger, talon.size());
        		gameState = 60;
        		refresh();
        	}
        	break;
        case 50: // Younger Discard Human
        	gameState = 60;
        	while (younger.size() < 12) {
        		younger.addCard(talon.takeTop());
        	}
        	refresh();
        	break;
        case 60: // Declarations
        	gameState = 70;
        	trickNum = 0;
        	lead = elder;
        	follow = younger;
        	buffer += "<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">";
        	break;
        case 70: // Lead Trick
        	if (lead.isHuman()) {
        		buffer += "Choose a card to lead";
        		gameState = 80;
        	} else {
            	lead.addScore(1);
        		leadCard = lead.askLead();
        		lead.removeCard(leadCard);
    			follow.markSeen(leadCard);
    			gameState = 90;
            	buffer += "<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">";
        	}
        	break;
        case 80: // Lead Trick Human
        	inputString = request.getParameter("c");
        	if (inputString != null) {
    			input = Integer.parseInt(inputString);
    		} else {
    			input = null;
    			gameState = 70;
            	buffer += "<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">";
            	break;
    		}
    		leadCard = lead.removeIndex(input);
			follow.markSeen(leadCard);
        	lead.addScore(1);
    		gameState = 90;
        	buffer += "<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">";
    		break;
        case 90: // Follow Trick
        	if (follow.isHuman()) {
        		buffer += "Choose a card to follow";
        		gameState = 100;
        	} else {
    			boolean valid = false;
    			while (!valid) {
    				valid = true;
    				followCard = follow.askFollow(leadCard);
    				if (followCard == null) {
    					valid = false;
    				} else if (followCard.getSuit() != leadCard.getSuit() && follow.hasSuit(leadCard.getSuit())) {
    					valid = false;
    				}
    			}
    			follow.removeCard(followCard);
    			gameState = 110;
            	buffer += "<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">";
        	}
        	break;
        case 100: // Follow Trick Human
        	inputString = request.getParameter("c");
        	if (inputString != null) {
    			input = Integer.parseInt(inputString);
    		} else {
    			input = null;
    			gameState = 90;
            	buffer += "<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">";
            	break;
    		}
        	followCard = follow.getIndex(input);
    		if (followCard.getSuit() != leadCard.getSuit() && follow.hasSuit(leadCard.getSuit())) {
    			buffer += "You must follow suit";
    		} else {
    			gameState = 110;
    			followCard = follow.removeIndex(input);
            	buffer += "<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">";
    		}
    		break;
        case 110: // Resolve Trick
        	if (cmp.compare(leadCard, followCard) > 0) {
    			lead.incTricks();
    		} else {
    			follow.incTricks();
    			follow.addScore(1);
    			Hand tmp = follow;
    			follow = lead;
    			lead = tmp;
    		}
        	gameState = 120;
        	refresh();
        	break;
        case 120: // View Results
        	if (lead.size() > 0) {
        		gameState = 70; // More tricks to play
            	buffer += "<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">";
        	} else {
        		gameState = 130;
            	refresh();
        	}
        	break;
        case 130: // New Hand
        	if (player1.getScore() > 99 || player2.getScore() > 99) {
        		gameState = 140;
            	gameOver = true;
        		refresh();
        		break;
        	}
        	player1.clear();
        	player2.clear();
        	Hand tmp = elder;
        	elder = younger;
        	younger = tmp;
        	gameState = 15;
        	out.println("<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">");
            break;
        case 140: // Game over
        	player1.clear();
        	player2.clear();
        	player1.clearScore();
        	player2.clearScore();
        	gameState = 0;
        	out.print("<form action=\"");
            out.print("WebPiquet\" ");
            out.println("method=POST>");
            out.print("<input type=submit value=\"");
            out.print("Play Again\">");
            out.println("</form></p>");
        	gameOver = false;
        	break;
        }
        if (gameState > 10) printStatus();
        out.println("</body>");
        out.println("</html>");
    }
	public void doPost(HttpServletRequest request, HttpServletResponse response)
    throws IOException, ServletException
    {
		doGet(request, response);
    }
}
