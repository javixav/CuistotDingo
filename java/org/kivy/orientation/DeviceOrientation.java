package org.kivy.orientation;
import org.kivy.android.PythonActivity;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.media.ExifInterface;

/**
 * source code :  https://gist.github.com/Abdelhady/501f6e48c1f3e32b253a#file-deviceorientation
 *
 * another alternative to this class's approach:
 * http://stackoverflow.com/questions/11175599/how-to-measure-the-tilt-of-the-phone-in-xy-plane-using-accelerometer-in-android/15149421#15149421
 *
 */

public class DeviceOrientation {
    private final int ORIENTATION_PORTRAIT = ExifInterface.ORIENTATION_ROTATE_90; // 6
    private final int ORIENTATION_LANDSCAPE_REVERSE = ExifInterface.ORIENTATION_ROTATE_180; // 3
    private final int ORIENTATION_LANDSCAPE = ExifInterface.ORIENTATION_NORMAL; // 1
    private final int ORIENTATION_PORTRAIT_REVERSE = ExifInterface.ORIENTATION_ROTATE_270; // 8

    int smoothness = 1;
    private float averagePitch = 0;
    private float averageRoll = 0;

    private int orientation = ORIENTATION_PORTRAIT; //6
    public boolean triumph = false; // xav

    private float[] pitches;
    private float[] rolls;

    Sensor accelerometer;
    Sensor magnetometer;
    Sensor vectorSensor; // strangely, this sensor seems to be irrelevent

    // Class constructor :
    public DeviceOrientation() {
        pitches = new float[smoothness];
        rolls = new float[smoothness];
    }

    public int getOrientation() {
        return orientation;
    }

    // Define a new listener
    class MySensorEventListener implements SensorEventListener {

    // SensorEventListener sensorEventListener = new SensorEventListener() {
        float[] mGravity;
        float[] mGeomagnetic;

        @Override
        public void onSensorChanged(SensorEvent event) {
            if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER)
                mGravity = event.values;
            if (event.sensor.getType() == Sensor.TYPE_MAGNETIC_FIELD)
                mGeomagnetic = event.values;
            if (mGravity != null && mGeomagnetic != null) {
                float R[] = new float[9];
                float I[] = new float[9];
                boolean success = SensorManager.getRotationMatrix(R, I, mGravity, mGeomagnetic);
                if (success) {
                    triumph = true;
                    float orientationData[] = new float[3];
                    SensorManager.getOrientation(R, orientationData);
                    averagePitch = addValue(orientationData[1], pitches);
                    averageRoll = addValue(orientationData[2], rolls);
                    orientation = calculateOrientation();
                }
                else
                    triumph = false;
            }
        }

        @Override
        public void onAccuracyChanged(Sensor sensor, int accuracy) {
            // TODO Auto-generated method stub
        }
    };

    // Instanciate a new listener
    MySensorEventListener mysensorEventListener = new MySensorEventListener();

    private float addValue(float value, float[] values) {
        value = (float) Math.round((Math.toDegrees(value)));
        float average = 0;
        for (int i = 1; i < smoothness; i++) {
            values[i - 1] = values[i];
            average += values[i];
        }
        values[smoothness - 1] = value;
        average = (average + value) / smoothness;
        return average;
    }

    private int calculateOrientation() {
        // finding local orientation dip
        if (((orientation == ORIENTATION_PORTRAIT || orientation == ORIENTATION_PORTRAIT_REVERSE)
                && (averageRoll > -30 && averageRoll < 30))) {
            if (averagePitch > 0)
                return ORIENTATION_PORTRAIT_REVERSE;
            else
                return ORIENTATION_PORTRAIT;
        } else {
            // divides between all orientations
            if (Math.abs(averagePitch) >= 30) {
                if (averagePitch > 0)
                    return ORIENTATION_PORTRAIT_REVERSE;
                else
                    return ORIENTATION_PORTRAIT;
            } else {
                if (averageRoll > 0) {
                    return ORIENTATION_LANDSCAPE_REVERSE;
                } else {
                    return ORIENTATION_LANDSCAPE;
                }
            }
        }
    }

    void sensorEnable(boolean enable) {

        // Create our listener
        Context context = (Context) PythonActivity.mActivity;
        SensorManager sm = (SensorManager) context.getSystemService(Context.SENSOR_SERVICE);
        accelerometer = sm.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        magnetometer = sm.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);

        if (accelerometer == null || magnetometer == null)
            return;
        
        if (enable) {
            sm.registerListener(mysensorEventListener, accelerometer, SensorManager.SENSOR_DELAY_UI);
            sm.registerListener(mysensorEventListener, magnetometer, SensorManager.SENSOR_DELAY_UI);
        }
        else 
            sm.unregisterListener(mysensorEventListener);
    }
}