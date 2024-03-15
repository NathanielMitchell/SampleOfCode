public class Stack<T> {

	// List running the background of Stack
	private List<T> l;
	// constructor
	public Stack() {
		this.l = new List<T>();
	}

	// copy constructor. Takes in a stack
	public Stack(Stack<T> s) {
		this.l = new List<T>(s.l);
		this.l.First();
	}

	// puts new data on the top of the stack
	public void Push(T data) {
		this.l.First();
		this.l.InsertBefore(data);
	}

	// returns the data at the top of the stack and deletes it
	public T Pop() {
		this.l.First();
		T returnValue = this.l.GetValue();
		this.l.Remove();
		return returnValue;
	}

	// returns the data on the top of the stack
	public T Peek() {
		this.l.First();
		return this.l.GetValue();
	}

	// returns the size of the stack
	public int Size() {
		return this.l.GetSize();
	}

	// returns true or false depending on if the stack is empty or not
	public boolean IsEmpty() {
		return this.l.IsEmpty();
	}

	// returns true or false depending on if the stack is full or not
	public boolean IsFull() {
		return this.l.IsFull();
	}

	// takes in a stack and returns true or false depending on whether or not the 
	// stack and input stack are the same
	public boolean Equals(Stack<T> s) {
		return this.l.Equals(s.l);
	}

	// takes in a stack and adds together the stack taken in and the current stack
	public Stack<T> Add(Stack<T> s) {
		Stack<T> r = new Stack<T>();
		r.l = new List<T>(this.l.Add(s.l));
		return r;
	}


	// toString method
	public String toString() {
		return l.toString();
	}
}
