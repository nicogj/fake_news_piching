
import numpy as np
from read_in_and_cleaning import load_data_and_clean, get_all_labels, get_all_headlines, get_all_bodies, get_dico_by_id, get_all_source
from models.doc2vec_utils import create_dataset, get_frequency_of_words, from_counter_occurences_to_counter_frequencies, plot_counter

class Param(object):

    def __init__(self):

        self.data = load_data_and_clean()
        self.data_by_id = get_dico_by_id(self.data)
        self.bodies = get_all_bodies(self.data_by_id)
        self.headlines = get_all_headlines(self.data_by_id)
        self.source = get_all_source(self.data_by_id)

        counter = get_frequency_of_words(self.bodies)
        print("Number of different words", len(counter))
        #counter_frequencies = from_counter_occurences_to_counter_frequencies(counter)
        #plot_counter(counter_frequencies, "headline_frequencies")
        
        self.vocabulary_size = 10000
        self.user_size = len(self.bodies)
        self.remove_top_n_words = 50
        self.window_size = 3
        self.lists, self.dictionnary_word_to_id, self.dictionnary_id_to_word, self.triplets = create_dataset(self, self.bodies)
        np.random.shuffle(self.triplets)
        
        print("Parameters")
        print("Vocab_size", self.vocabulary_size, "User_size", self.user_size, "Number of pairs", len(self.triplets))
        self.number_of_training_pairs = len(self.triplets)
        self.valid_ids = np.array([10, 20, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])

        self.training_steps = 50000
        self.index = 0
        self.batch_size = 128
        self.num_sampled = int(50)
        self.learning_rate = 2.5e-3
        self.print_loss_every = 200
        self.print_valid_every = 2500
        self.save_embeddings_every = 2500
        self.word_embedding_size = 150
        self.doc_embedding_size = 150


        
