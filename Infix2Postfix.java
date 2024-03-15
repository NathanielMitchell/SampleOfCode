import java.io.*;

public class Infix2Postfix {
	public static void main (String[] args) {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		try{
		String line = "";
		while ((line = br.readLine()) != null) {
			Queue<Character> infixQ = new Queue<Character>();
			for (int i = 0; i < line.length(); i++){
				infixQ.Enqueue(line.charAt(i));
			}
			Queue<Character> postFixQ = new Queue<Character>();
			Stack<Character> operS = new Stack<Character>();
			Character op;
			Character token;
			while (!infixQ.IsEmpty()) {
				token = infixQ.Dequeue();
				if(!isOperator(token)) {
					postFixQ.Enqueue(token);
				} else if (token == ')') {
					op = operS.Pop();
					while (op != '(') {
						postFixQ.Enqueue(op);
						op = operS.Pop();
					}
				} else {
					op = operS.Peek();
					while (postfixPriority(op) >= infixPriority(token)) {
						op = operS.Pop();
						postFixQ.Enqueue(op);
						op = operS.Peek();
					}
					operS.Push(token);
				}
			}
			while (!operS.IsEmpty()) {
				op = operS.Pop();
				postFixQ.Enqueue(op);
			}
		System.out.println(line);
		System.out.println(postFixQ);
		System.out.println(postfixEvaluator(postFixQ));
		System.out.println();
		}
		br.close();
		} catch (IOException e) {
			System.out.println(e);
		}
	}

	public static int infixPriority(Character token) {
		if (token == null)
			return 0;
		String operators = "(^*/+-";
		int values[] = {4, 3, 2, 2, 1, 1};
		int i;
		if ((i = operators.indexOf(token)) != -1)
			return values[i];
		else
			return 0;
	}

	public static int postfixPriority(Character op) {
		if (op == null)
			return 0;
		String operators = "^*/+-";
		int values[] = {2, 2, 2, 1, 1};
		int i;
		if ((i = operators.indexOf(op)) != -1) 
			return values[i];
		else
			return 0;

	}

	public static boolean isOperator(Character token) {
		String operators = "()^*/+-";
		for (int i = 0; i < operators.length(); i++) {
			if (token == operators.charAt(i))
				return true;
		}
		return false;
	}

	public static float postfixEvaluator(Queue<Character> postfixQ) {
		Stack<Float> evalStack = new Stack<Float>();
		Character deqOp;
		String operators = "^*/+-";
		float a, b;
		while (!postfixQ.IsEmpty()) {
			deqOp = postfixQ.Dequeue();
			if (!isOperator(deqOp)) {
				evalStack.Push((float)Character.getNumericValue(deqOp));
			} else {
				for (int i = 0; i < operators.length(); i++) {
					if (operators.charAt(i) == deqOp) {
						b = evalStack.Pop();
						a = evalStack.Pop();
						float[] funcs = {power(a, b), mult(a, b), div(a, b), add(a, b), sub(a, b)};
						evalStack.Push(funcs[i]);
					}
				}
			}
		}
		return evalStack.Pop();
	}

	public static float add(float a, float b) {
		return a + b;
	}

	public static float sub(float a, float b) {
		return a - b;
	}

	public static float mult(float a, float b) {
		return a * b;
	}

	public static float div(float a, float b) {
		return a / b;
	}

	public static float power(float a, float b) {
		return (float)Math.pow(a, b);
	}
}
