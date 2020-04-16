import java.io.*;
import java.util.HashMap;

import javax.servlet.*;
import javax.servlet.http.*;

public class WebPiquet extends HttpServlet {
	public HashMap<String, WebPiquetGame> gameList;
	public WebPiquetGame game;
	public String name;
	public boolean needCookie;
	public LeaderBoard scoreList;
	public boolean init;
	
	public WebPiquet() throws FileNotFoundException {
		gameList = new HashMap<String, WebPiquetGame>();
		scoreList = new LeaderBoard();
		init = true;
	}
	public void doGet(HttpServletRequest request, HttpServletResponse response)
    throws IOException, ServletException
    {
		response.setContentType("text/html");
		PrintWriter out = response.getWriter();
		if (init) {
			scoreList.setPath(getServletContext().getRealPath("./LeaderBoard.txt"));
			init = false;
		}
		if (gameList.size() > 100) {
			out.println("Something really bad is happening, please tell Orion");
		}
		Cookie[] cookies = request.getCookies();
		name = request.getParameter("name");
		game = null;
		needCookie = true;
		if (cookies != null) {
			for (int i = 0; i < cookies.length; i++) {
				Cookie c = cookies[i];
				String key = c.getName();
				String value = c.getValue();
				if ("name".equals(key)) {
					name = value;
					game = gameList.get(name);
					needCookie = false;
					break;
				}
			}
		}
		if (name == null) {
			out.println("<html>");
			out.println("<body>");
			out.println("<head>");
			out.println("<title>WebPiquet</title>");
			out.println("</head>");
			out.println("<body>");
			out.println("<h1>Welcome to WebPiquet</h1>");
			out.print("<form action=\"");
			out.print("WebPiquet\" ");
			out.println("method=POST>");
			out.println("Name:");
			out.println("<input type=text size=20 name=name>");
			out.println("<br>");
			out.println("<input type=submit value=\"Log in\">");
			out.println("</form>");
			out.println("</body>");
			out.println("</html>");
		} else if (needCookie) {
			response.addCookie(new Cookie("name",name));
			Entry scoreEnt = scoreList.lookup(name);
			if (scoreEnt != null) {
				gameList.put(name, new WebPiquetGame(name));
				out.println("<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">");
			} else {
				gameList.put(name, new WebPiquetGame(name));
				out.println("<meta http-equiv=\"refresh\" content=\"0;URL=http://sauter.bounceme.net:8080/servlet/WebPiquet\">");
			}
		} else {
			if (game == null) {
				game = new WebPiquetGame(name);
				gameList.put(name, game);
			}
			if (game.gameOver) {
				String opponent = game.player2.getName();
				Entry playerScoreEnt = scoreList.lookup(name);
				Entry oppScoreEnt = scoreList.lookup(opponent);
				Integer playerPrevScore = 0;	//Previous top scores
				Integer oppPrevScore = 0;
				Integer totalPlayerScore = 0;	//Previous total scores
				Integer totalOppScore = 0;
				if (playerScoreEnt != null) {	//If player has entry read out previous values
					playerPrevScore = playerScoreEnt.getTop();
					totalPlayerScore = playerScoreEnt.getTotal();
				}
				if (oppScoreEnt != null) {
					oppPrevScore = oppScoreEnt.getTop();
					totalOppScore = oppScoreEnt.getTotal();
				}
				Integer finalScore = game.getFinalScore();
				Integer oppScore = 0;
				if (finalScore < 0) {	//Negative score means computer won
					oppScore = -1*finalScore;
					finalScore = 0;
				}
				totalPlayerScore += finalScore;
				totalOppScore += oppScore;
				if (finalScore < playerPrevScore) {
					finalScore = playerPrevScore;
				}
				if (oppScore < oppPrevScore) {
					oppScore = playerPrevScore;
				}
				if (!game.watch) {
					scoreList.update(name, totalPlayerScore, finalScore);
					scoreList.update(opponent, totalOppScore, oppScore);
				} else {
					out.println("No score has been recorded");
				}
				out.println("<h1>Game Over</h1><br>");
				out.println("<h2>High Scores</h2><br>");
				out.println("  <table width=\"400\">");
				out.println("    <tr>");
				out.println("      <td><b>Player</b></td>");
				out.println("      <td><b>Average Score</b></td>");
				out.println("      <td><b>Top Score</b></td>");
				out.println("    </tr>");
				for (Entry e: scoreList.getList()) {
					out.println("    <tr>");
					out.println("      <td>"+e.getName()+"</td>");
					float avg = e.getTotal()/e.getGames();
					out.println("      <td>"+avg+"</td>");
					out.println("      <td>"+e.getTop()+"</td>");
					out.println("    </tr>");
				}
				out.println("  </table><br><br>");
			}
			try {
				game.doGet(request, response);
			} catch (Exception e) {
				out.println("<h1>Error</h1><br>");
				out.println("The following error occurred:<br>");
				out.println(e+"<br><br>");
				out.println("<!--");
				e.printStackTrace(out);
				out.println("-->");
				game = new WebPiquetGame(name);
				gameList.put(name, game);
				out.println("<a href=\"WebPiquet\">Game restarted. Click here to continue.</a><br>");
			}
		}
    }
	
public void doPost(HttpServletRequest request, HttpServletResponse response)
throws IOException, ServletException
	{
		doGet(request, response);
    }
	
}
