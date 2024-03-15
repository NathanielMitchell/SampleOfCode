public class Queue<T> {
	
	// the list in the backend of the queue
	private List<T> l;

	// constructor
	public Queue() {
		this.l = new List<T>();
	}

	// copy constructor takes in a queue
	public Queue(Queue<T> q) {
		this.l = new List<T>(q.l);
	}

	// inserts an item at the end of the queue
	public void Enqueue(T data) {
		this.l.Last();
		this.l.InsertAfter(data);
	}

	// removes the item at the beginning of the list and removes it
	public T Dequeue() {
		this.l.First();
		T returnData = this.l.GetValue();
		this.l.Remove();
		return returnData;
	}

	// returns the item at the beginning of the queue but does not remove it
	public T Peek() {
		this.l.First();
		return this.l.GetValue();
	}

	// returns the size of the queue
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

	// returns true or false depending on if the current queue and a queue taken in are equal
	public boolean Equals(Queue<T> q) {
		return this.l.Equals(q.l);
	}

	// Adds two queues together starting with the current and adding the one taken in
	public Queue<T> Add(Queue<T> q) {
		Queue<T> r = new Queue<T>();
		r.l = this.l.Add(q.l);
		return r;
	}

	// to string function
	public String toString() {
		return l.toString();
	}
}
