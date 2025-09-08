import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, Conv2DTranspose, MaxPooling2D, concatenate, Input, Dropout, Add
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import backend as K
from keras.losses import BinaryCrossentropy

K.set_image_data_format('channels_last')

smooth = 1e-5


def dice_coef(y_true, y_pred):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)


def dice_loss(y_true, y_pred):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (1 - (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth))


def IoU(y_true, y_pred):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    union = K.sum(y_true_f) + K.sum(y_pred_f) - intersection
    return (intersection + smooth) / (union + smooth)


def weighted_bce(y_true, y_pred):
    y_true_flat = K.flatten(y_true)
    y_pred_flat = K.flatten(y_pred)
    indices_true = tf.where(tf.equal(y_true_flat, 1))
    indices_false = tf.where(tf.equal(y_true_flat, 0))
    y_pred_true = tf.gather(y_pred_flat, indices=indices_true)
    y_pred_false = tf.gather(y_pred_flat, indices=indices_false)
    bce = tf.keras.losses.BinaryCrossentropy()
    bce_ones = bce(tf.ones_like(y_pred_true), y_pred_true)
    bce_zeros = bce(tf.zeros_like(y_pred_false), y_pred_false)
    bce_ones_score = tf.reduce_mean(bce_ones)
    bce_zeros_score = tf.reduce_mean(bce_zeros)
    total_elements = tf.size(y_true_flat)
    ones_size = tf.reduce_sum(y_true_flat)
    zeros_size = total_elements - ones_size
    def select_balanced():
        return (bce_ones_score + bce_zeros_score) / 2
    return tf.cond(tf.equal(ones_size, 0), lambda: bce_zeros_score,
                   lambda: tf.cond(tf.equal(zeros_size, 0), lambda: bce_ones_score, select_balanced))


def composite_loss(y_true, y_pred):
    BCE_weight = 0.25
    dl_weight = 0.75
    bce_score = weighted_bce(y_true, y_pred)
    dl = dice_loss(y_true, y_pred)
    return BCE_weight * bce_score + dl_weight * dl


def rec_layer(layer, filters):
    reconv1 = Conv2D(filters, (3, 3), activation='relu', padding='same')(layer)
    layer_add = Conv2D(filters, kernel_size=(1, 1), padding='same')(layer)
    add_conv1 = Add()([reconv1, layer_add])
    reconv1 = Conv2D(filters, (3, 3), activation='relu', padding='same')(add_conv1)
    add_conv2 = Add()([reconv1, layer_add])
    reconv1 = Conv2D(filters, (3, 3), activation='relu', padding='same')(add_conv2)
    return reconv1


IMAGE_ROWS = 192
IMAGE_COLS = 192
IMAGE_DEPTH = 1


def r2udensenet():
    inputs = Input((IMAGE_ROWS, IMAGE_COLS, IMAGE_DEPTH))
    conv1 = rec_layer(inputs, 32)
    conv1 = rec_layer(conv1, 32)
    conv1add = Conv2D(32, kernel_size=(1, 1), padding='same')(inputs)
    add1 = Add()([conv1add, conv1])
    dense1 = concatenate([add1, conv1], axis=3)
    pool1 = MaxPooling2D(pool_size=(2, 2))(dense1)

    conv2 = rec_layer(pool1, 64)
    conv2 = rec_layer(conv2, 64)
    conv2add = Conv2D(64, kernel_size=(1, 1), padding='same')(pool1)
    add2 = Add()([conv2add, conv2])
    dense2 = concatenate([add2, conv2], axis=3)
    pool2 = MaxPooling2D(pool_size=(2, 2))(dense2)

    conv3 = rec_layer(pool2, 128)
    conv3 = rec_layer(conv3, 128)
    conv3add = Conv2D(128, kernel_size=(1, 1), padding='same')(pool2)
    add3 = Add()([conv3add, conv3])
    dense3 = concatenate([add3, conv3], axis=3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(dense3)

    conv4 = rec_layer(pool3, 256)
    conv4 = rec_layer(conv4, 256)
    conv4add = Conv2D(256, kernel_size=(1, 1), padding='same')(pool3)
    add4 = Add()([conv4add, conv4])
    dense4 = concatenate([add4, conv4], axis=3)
    drop4 = Dropout(0.5)(dense4)
    pool4 = MaxPooling2D(pool_size=(2, 2))(dense4)

    conv5 = rec_layer(pool4, 512)
    conv5 = rec_layer(conv5, 512)
    conv5add = Conv2D(512, kernel_size=(1, 1), padding='same')(pool4)
    add5 = Add()([conv5add, conv5])
    dense5 = concatenate([add5, conv5], axis=3)
    drop5 = Dropout(0.5)(dense5)

    up6 = concatenate([Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same')(dense5), conv4], axis=3)
    conv6 = rec_layer(up6, 256)
    conv6 = rec_layer(conv6, 256)
    conv6add = Conv2D(256, kernel_size=(1, 1), padding='same')(up6)
    add6 = Add()([conv6add, conv6])
    dense6 = concatenate([add6, conv6], axis=3)

    up7 = concatenate([Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(dense6), conv3], axis=3)
    conv7 = rec_layer(up7, 128)
    conv7 = rec_layer(conv7, 128)
    conv7add = Conv2D(128, kernel_size=(1, 1), padding='same')(up7)
    add7 = Add()([conv7add, conv7])
    dense7 = concatenate([add7, conv7], axis=3)

    up8 = concatenate([Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(dense7), conv2], axis=3)
    conv8 = rec_layer(up8, 64)
    conv8 = rec_layer(conv8, 64)
    conv8add = Conv2D(64, kernel_size=(1, 1), padding='same')(up8)
    add8 = Add()([conv8add, conv8])
    dense8 = concatenate([add8, conv8], axis=3)

    up9 = concatenate([Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same')(dense8), conv1], axis=3)
    conv9 = rec_layer(up9, 64)
    conv9 = rec_layer(conv9, 64)
    conv9add = Conv2D(64, kernel_size=(1, 1), padding='same')(up9)
    add9 = Add()([conv9add, conv9])
    dense9 = concatenate([add9, conv9], axis=3)

    conv10 = Conv2D(1, (1, 1), activation='sigmoid')(dense9)
    model = Model(inputs=[inputs], outputs=[conv10])
    model.compile(optimizer=Adam(learning_rate=1e-5), loss=composite_loss,
                  metrics=[BinaryCrossentropy(name='rawBinaryCE'), weighted_bce, dice_loss, dice_coef, IoU])
    return model


