from models.word2vec_utils import get_frequency_of_words, create_dataset, generate_batch_data
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import numpy as np
import os
import json
import random
import pandas as pd

def create_and_train_word2vec_model(param):

    random.seed(param.seed)
    counter = get_frequency_of_words(param.text)
    vocabulary_size = min(param.max_vocabulary_size, len(counter)-param.remove_top_n_words)
    lists, dictionnary_id_to_word, triplets = create_dataset(param, vocabulary_size, counter)
    np.random.seed(param.seed)
    np.random.shuffle(triplets)

    print("\nParameters:")
    print("Number of Texts: ", len(param.text))
    print("Words Count: ", len([item for sublist in param.text for item in sublist]))
    print("Unique Words: ", len(counter))
    print("Vocabulary Size: ", vocabulary_size)
    print("Number of Pairs: ", len(triplets))
    print("Most Common Words: ", counter.most_common()[:param.print_most_common])

    valid_ids = np.array(random.sample(range(0, vocabulary_size), param.nb_eval_words))

    # Start a graph session
    tf.set_random_seed(param.seed)
    sess = tf.Session()
    tf.set_random_seed(param.seed)
    print('\nCreating Model')

    # Define Embeddings:
    word_embeddings = tf.Variable(tf.random_uniform([vocabulary_size, param.word_embedding_size], -1.0, 1.0))
    tf.set_random_seed(param.seed)

    # NCE loss parameters
    nce_weights = tf.Variable(tf.truncated_normal([vocabulary_size, param.word_embedding_size], stddev=1.0/np.sqrt(param.word_embedding_size)))
    tf.set_random_seed(param.seed)
    nce_biases = tf.Variable(tf.zeros([vocabulary_size]))
    tf.set_random_seed(param.seed)

    # Create data/target placeholders
    word_inputs = tf.placeholder(tf.int32, shape=[None])
    tf.set_random_seed(param.seed)
    word_targets = tf.placeholder(tf.int32, shape=[None,1])
    tf.set_random_seed(param.seed)
    valid_dataset = tf.constant(valid_ids, dtype=tf.int32)
    tf.set_random_seed(param.seed)

    # Lookup the word embedding
    # Add together element embeddings in window:
    embed_words = tf.nn.embedding_lookup(word_embeddings, word_inputs)
    tf.set_random_seed(param.seed)

    # Get loss from prediction
    loss = tf.reduce_mean(tf.nn.sampled_softmax_loss(nce_weights, nce_biases, word_targets, embed_words, param.num_sampled, vocabulary_size))
    tf.set_random_seed(param.seed)

    # Create optimizer
    optimizer = tf.train.AdamOptimizer(learning_rate=param.learning_rate)
    tf.set_random_seed(param.seed)
    train_step = optimizer.minimize(loss)
    tf.set_random_seed(param.seed)

    # Cosine similarity between words
    norm = tf.sqrt(tf.reduce_sum(tf.square(word_embeddings), 1, keepdims=True))
    tf.set_random_seed(param.seed)
    normalized_embeddings = word_embeddings / norm
    valid_embeddings = tf.nn.embedding_lookup(normalized_embeddings, valid_dataset)
    tf.set_random_seed(param.seed)
    similarity = tf.matmul(valid_embeddings, normalized_embeddings, transpose_b=True)
    tf.set_random_seed(param.seed)

    # Create model saving operation
    saver = tf.train.Saver({"word_embeddings": word_embeddings})
    tf.set_random_seed(param.seed)

    # Add variable initializer.
    init = tf.global_variables_initializer()
    tf.set_random_seed(param.seed)
    sess.run(init)
    tf.set_random_seed(param.seed)

    # Run the skip gram model.
    print('Starting Training')
    iter, loss_vec = [], []
    for i in range(param.training_steps):
        tf.set_random_seed(param.seed)
        batch = generate_batch_data(param, triplets)
        word_i, doc_i, word_t = batch[:,0], batch[:,1], np.reshape(batch[:,2], (-1,1))
        feed_dict = {word_inputs: word_i, word_targets: word_t}

        # Run the train step
        _, loss_val = sess.run([train_step, loss], feed_dict=feed_dict)
        iter.append(i+1)
        loss_vec.append(loss_val)

        # Return the loss
        if (i + 1) % param.print_loss_every == 0:
            loss_val = sess.run(loss, feed_dict=feed_dict)
            print('{} last losses at step {}: {}'.format(param.print_loss_every, i+1, sum(loss_vec[-param.print_loss_every:])/param.print_loss_every))

        # Validation: Print some random words and top related words
        if (i + 1) % param.print_valid_every == 0:
            sim = sess.run(similarity, feed_dict=feed_dict)
            for j in range(len(valid_ids)):
                valid_word = dictionnary_id_to_word[valid_ids[j]]
                # top_k = 5  # number of nearest neighbors
                nearest = (-sim[j, :]).argsort()[1:param.k_nearest_neighbors + 1]
                log_str = "Nearest to {}:".format(valid_word)
                for k in range(param.k_nearest_neighbors):
                    close_word = dictionnary_id_to_word[nearest[k]]
                    log_str = '{} {},'.format(log_str, close_word)
                print(log_str)

        # Save dictionary + embeddings + loss_vec
        if ((i + 1) % param.save_embeddings_every == 0) or ((i + 1) % param.training_steps == 0):
            np.save("data/{}.npy".format(param.file_name), sess.run(word_embeddings))
            f = open("data/{}_dict.json".format(param.file_name), "w")
            f.write(json.dumps(dictionnary_id_to_word))
            f.close()
            pd.DataFrame({
                'iteration': iter,
                'loss_value':loss_vec
            }).to_csv('data/{}_loss_values.csv'.format(param.file_name), index=False)

    return loss_vec
