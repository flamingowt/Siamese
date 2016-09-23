import numpy as np
from keras.models import Sequential
from keras.optimizers import SGD, RMSprop
from keras.layers.core import Dense, Dropout, Activation
from keras.callbacks import EarlyStopping
import createShapeData
import matplotlib as mlp
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn import cross_validation

x_train, x_test, y_train, y_test = createShapeData.get_shape_data(.70)

model_a = Sequential()
model_a.add(Dense(200, input_shape=(x_train.shape[1],)))
model_a.add(Activation('linear'))
model_a.add(Dropout(.25))
model_a.add(Dense(100))
model_a.add(Activation('linear'))
model_a.add(Dropout(.25))
model_a.add(Dense(50))
model_a.add(Activation('linear'))
rms = RMSprop()
model_a.compile(loss='siamese_euclidean', optimizer=rms)

mini_batch = 20
no_epoch = 10
model_a.fit(x_train, y_train, batch_size=mini_batch, nb_epoch=no_epoch, verbose=1,
          show_accuracy=True, validation_split=.25, callbacks=[EarlyStopping(monitor='val_loss', patience=2)])

y_ts_est = model_a.predict(x_test, batch_size=mini_batch)
pair_errors = ((y_ts_est[0::2] - y_ts_est[1::2]) ** 2).sum(axis=1, keepdims=True)
print('replicating the loss for training: ' + str(((pair_errors - y_test[0::2])**2).mean()))

# plot pair errors
pair_error_median = np.median(pair_errors)
threshold = pair_error_median*.01
plt.plot(pair_errors)
plt.hold(True)
plt.plot(threshold*np.ones(pair_errors.shape), 'r')
plt.savefig('pair_errors.png')
plt.hold(False)

label = np.zeros(pair_errors.shape)
for i in range(int(y_ts_est.shape[0]/2)):
    if pair_errors[i] > threshold:
        label[i] = 0
    else:
        label[i] = 1

y_test_norep = y_test[0::2]
y_est_norep = label
print("accuracy is: " + str(accuracy_score(y_test_norep, y_est_norep)))
print("confusion matrix:")
print(confusion_matrix(y_test_norep, y_est_norep))