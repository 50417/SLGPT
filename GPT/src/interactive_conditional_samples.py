#!/usr/bin/env python3

import fire
import json
import os
import numpy as np
import tensorflow as tf
from distutils.dir_util import copy_tree
import shutil

import model, sample, encoder

def interact_model(
    model_name='124M',
    seed=None,
    nsamples=1000,
    batch_size=1,
    length=None,
    temperature=1,
    top_k=0,
    top_p=0.0
):
    """
    Interactively run the model
    :model_name=117M : String, which model to use
    :seed=None : Integer seed for random number generators, fix seed to reproduce
     results
    :nsamples=1 : Number of samples to return total
    :batch_size=1 : Number of batches (only affects speed/memory).  Must divide nsamples.
    :length=None : Number of tokens in generated text, if None (default), is
     determined by model hyperparameters
    :temperature=1 : Float value controlling randomness in boltzmann
     distribution. Lower temperature results in less random completions. As the
     temperature approaches zero, the model will become deterministic and
     repetitive. Higher temperature results in more random completions.
    :top_k=0 : Integer value controlling diversity. 1 means only 1 word is
     considered for each step (token), resulting in deterministic completions,
     while 40 means 40 words are considered at each step. 0 (default) is a
     special setting meaning no restrictions. 40 generally is a good value.
    :top_p=0.0 : Float value controlling diversity. Implements nucleus sampling,
     overriding top_k if set to a value > 0. A good setting is 0.9.
    """
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0
    if not os.path.isdir(os.path.join('models',model_name)):
        os.mkdir(os.path.join('models',model_name))
    copy_tree(os.path.join('checkpoint',model_name),os.path.join('models',model_name))
    files = ['encoder.json','hparams.json','vocab.bpe']
    for f in files:
        shutil.copy(os.path.join('models','124M',f), os.path.join('models',model_name))
    enc = encoder.get_encoder(model_name)
    hparams = model.default_hparams()
    with open(os.path.join('models', model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
        print(length)
    #elif length > hparams.n_ctx:
    #   raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)
    #config = tf.ConfigProto(device_count={'GPU': 0})
    config = tf.ConfigProto()
    with tf.Session(graph=tf.Graph(),config=config) as sess:
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        raw_text = """Model {"""
                   #input("Model prompt >>> ")
        context_tokens = enc.encode(raw_text)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join('models', model_name))
        saver.restore(sess, ckpt)
        from datetime import datetime
        #while True:
        generated = 0
        import time
        grand_start = time.time()
        for cnt in range(nsamples // batch_size):
            start_per_sample = time.time()
            output_text = raw_text
            text = raw_text
            context_tokens = enc.encode(text)
            #raw_text = input("Model prompt >>> ")
            # while not raw_text:
            #     print('Prompt should not be empty!')
            #     raw_text = input("Model prompt >>> ")

            #print(context_tokens)
            #file_to_save.write(raw_text)	

            #for cnt in range(nsamples // batch_size):
            while "<|endoftext|>" not in text:
                out = sess.run(output, feed_dict={context: [context_tokens for _ in range(batch_size)]})[:,
                  len(context_tokens):]

                for i in range(batch_size):
                #generated += 1
                    text = enc.decode(out[i])


                if "<|endoftext|>" in text:
                    sep = "<|endoftext|>"
                    rest = text.split(sep, 1)[0]
                    output_text += rest
                    break
                context_tokens = enc.encode(text)
                output_text += text


            print("=" * 40 + " SAMPLE " + str(cnt) + " " + "=" * 40)
            minutes, seconds = divmod(time.time() - start_per_sample, 60)
            print("Output Done : {:0>2}:{:05.2f}".format(int(minutes),seconds) )
            print("=" * 80)
            with open("Simulink_sample/sample__"+str(cnt)+".mdl","w+") as f:
                f.write(output_text)
        elapsed_total = time.time()-grand_start
        hours, rem = divmod(elapsed_total,3600)
        minutes, seconds = divmod(rem, 60)
        print("Total time to generate 1000 samples :{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
if __name__ == '__main__':
    fire.Fire(interact_model)
