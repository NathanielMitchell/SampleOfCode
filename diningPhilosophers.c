#include <stdio.h>
#include <stdlib.h>
#include <semaphore.h>
#include <pthread.h>
#include <unistd.h>

// fairness is the number of times a process can be allowed to run ahead of other processes
#define FAIRNESS 9

// define a structure to store the semaphore and information about each philosopher
struct philoInfo {
    unsigned long *philoID; // to pass the philosopher his evenness or oddness
    int philoNum;
    int eatNum;
    long *numEaten; //array for number of times the philosopher has eaten
    sem_t *forks; // array of forks semaphores
};

// prototypes
void *philosopher(void *);
void init(struct philoInfo *PI, int philoNum, int eatNum);

int main (int argc, char *argv[]) {
    
    // usage 
    if (argc != 3) {
        printf("usage: ./a.out philosipher# eatingtimes");
        exit(1);
    }

    // store number of philosophers and times to eat as variables
    int philoNum = atoi(argv[1]);
    int eatNum = atoi(argv[2]);

    //define and initialize the struct of philosophers
    struct philoInfo PI;
    init(&PI, philoNum, eatNum); // initializing the eatNum and forks array

    // create an array of thread identifiers for each philosopher
    pthread_t philos[philoNum];

    // loop through each philospher to get even/odd identity for each philospher based on thread ID
    for (int i = 0; i < philoNum; i++) {
        pthread_create(&philos[i], NULL, philosopher, &PI);
        PI.philoID[i] = philos[i];
    }

    // wait for each thread to terminate before returning
    for (int i = 0; i < philoNum; i++) {
        pthread_join(philos[i], NULL);
    }
    return 0;

}

// initialization function for the philosophers struct
void init(struct philoInfo *PI, int philoNum, int eatNum) {

    if (philoNum == 1) {
        PI -> forks = (sem_t *)malloc(sizeof(sem_t) * (philoNum +1) ); // we still need two semaphore chopsticks if there is one philosopher
    } else {
        PI -> forks = (sem_t *)malloc(sizeof(sem_t) * philoNum); // semaphore, if multiple philosophers assign chopsticks to the same number of philosophers
    }
    PI -> eatNum = eatNum; // number of times each philosopher will eat
    PI -> philoID = (unsigned long *)malloc(sizeof(unsigned long) * philoNum); // array of IDs to get even/odd and number for each philosopher
    PI -> philoNum = philoNum; // number of philosophers
    // initialize the semaphore for each chopstick
    for (int i = 0; i < philoNum; i++) {
        sem_init(&PI -> forks[i], 0, 1);
    }
    if (philoNum == 1)
        sem_init(&PI -> forks[1], 0, 1);
    PI-> numEaten = (long *)malloc(sizeof(long)*philoNum); // array to store the number each process has eaten so far for comparisons to ensure fairness

}

void *philosopher(void * param) {
    
    // cast param to the structure
    struct philoInfo *PI = (struct philoInfo*)param;
    // declare an identifier for the current philosopher
    int identifier;

    // assign the identifier to the correct philosopher by locating the current thread in the ID array
    for (int i = 0; i < PI -> philoNum; i++) {
        if(PI->philoID[i] == pthread_self()) {
            identifier = i;
        }
    }
    
    // initialize the number of times this process has eaten to 0
    PI -> numEaten[identifier] = 0;
    // create a flag to think if the philospher has eaten too much
    unsigned char proceed;

    // continue looping until the philosopher is done eating
    while(PI -> numEaten[identifier] < PI -> eatNum) {
        // loop through the number of times each philosopher has eaten
        // to ensure it is not FAIRNESS greater than any other philosopher
    	for (int i = 0; i < PI -> philoNum; i++)
    	{
            // if the current is greater, set flag false
    		if (PI -> numEaten[identifier] > PI -> numEaten[i] + FAIRNESS)
   			    proceed = 0;

            // if not, set flag true
            else
                proceed = 1;
    	}
      
        // if the current thread is "even" and it is fair, current philosopher eats
        if(((identifier + 1) % 2) == 0 && proceed){
           
            // decrement the chopsticks to either side, modding by number of philosophers
            sem_wait(&PI -> forks[identifier]);
            sem_wait(&PI -> forks[(identifier + 1) % PI -> philoNum]);

        // if the current thread is "odd" and it is fair
        } else if (proceed) {

            // decrement the chopsticks to either side, modding by number of philosophers
            sem_wait(&PI -> forks[(identifier + 1) % PI -> philoNum]);
            
            if (PI -> philoNum == 1)
                sem_wait(&PI -> forks[(identifier + 1)]);
            else
                sem_wait(&PI -> forks[(identifier)]);

        }
     
        // print that the philosopher has eaten and increment the amount of times it has eaten, then sleep for eating
        printf("Philosopher %d is eating...\n", identifier + 1);
        PI -> numEaten[identifier]++;
        sleep(1); // eating

        // now increment the chopsticks because the philosopher is done eating
        // they need to be done in this order if the philosopher is even numbered
        if(((identifier + 1) % 2) == 0 && proceed) {

            sem_post(&PI -> forks[identifier]);
            sem_post(&PI -> forks[(identifier + 1) % PI -> philoNum]);

        // they need to be done in this order if the philosopher is odd numbered
        } else if (proceed){

            sem_post(&PI -> forks[(identifier + 1) % PI -> philoNum]);
            if (PI -> philoNum == 1)
                sem_post(&PI -> forks[identifier + 1]);
            else
                sem_post(&PI -> forks[identifier]);

        }
        // now the philosopher can think if it is done eating or if it was not able to eat due to fairness constraints
        printf("Philosopher %d is thinking...\n", identifier + 1);
        sleep(1); // thinking
    }
}

